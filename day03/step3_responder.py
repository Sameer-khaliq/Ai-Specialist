from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
# Final schema — yeh poora output structure hai
class FinalResponse(BaseModel):
    original_input: str = Field(description="The original raw user input")
    rewritten_input: str = Field(description="The cleaned, formal version")
    category: Literal["technical", "billing", "general", "urgent"] = Field(
        description="Support category"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Response priority level"
    )
    response_message: str = Field(
        description="The actual response to send to the user"
    )
    escalate_to_human: bool = Field(
        description="Whether this needs human agent"
    )

parser = JsonOutputParser(pydantic_object=FinalResponse)

respond_prompt = ChatPromptTemplate.from_template("""
You are a helpful customer support agent.
Given the support request details, generate a complete structured response.

{format_instructions}

Original input: {original_input}
Cleaned input: {rewritten_input}
Category: {category}

Generate a helpful response and determine priority and escalation.
""")



responder_chain = (
    respond_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)

if __name__ == "__main__":
    result = responder_chain.invoke({
        "original_input": "plz help i cant login",
        "rewritten_input": "Please help me. I am unable to log in to my account.",
        "category": "technical"
    })
    print("Response:", result)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import json

#all libraries required are imported
load_dotenv()

llm_precise = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0) # for stage1(rewriting) and stage2(classifying)
llm_creative = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3) # for stage 3(responding)

# structures

class ClassificationOutput(BaseModel):
    category: Literal["technical", "billing", "general", "urgent"]
    confidence: float = Field(ge=0.0, le=1.0)
    keywords: list[str]

class FinalResponse(BaseModel):
    original_input: str
    rewritten_input: str
    category: Literal["technical", "billing", "general", "urgent"]
    priority: Literal["low", "medium", "high", "critical"]
    response_message: str
    escalate_to_human: bool

# step1
# Rewriting the prompt
rewrite_prompt = ChatPromptTemplate.from_template("""
Rewrite this user input to be clear, formal, and grammatically correct.
Return ONLY the rewritten text, nothing else.

Input: {raw_input}
""")

rewriter = rewrite_prompt | llm_precise | StrOutputParser()

#step2
# Classifying the problem
classify_parser = JsonOutputParser(pydantic_object = ClassificationOutput)

classify_prompt = ChatPromptTemplate.from_template("""
Classify this support request. {format_instructions}
Request: {rewritten_input}""")

classifier = classify_prompt.partial(format_instructions = classify_parser.get_format_instructions()) | llm_precise | classify_parser
             
#step 3
#response
responder_parser = JsonOutputParser(pydantic_object = FinalResponse)
respond_prompt = ChatPromptTemplate.from_template("""
Generate a complete support response. {format_instructions}
Original: {original_input}
Cleaned: {rewritten_input}
Category: {category}""")
responder = (
    respond_prompt.partial(format_instructions=responder_parser.get_format_instructions())
    | llm_creative
    | responder_parser
)


#______Pipeline Execution_______
def run_pipeline(raw_input: str) ->dict:
    print(f"\nInput: {raw_input}")
    #step 1

    rewritten = rewriter.invoke({"raw_input": raw_input})
    print(f"Step1 -Rewritten prompt: ,{rewritten}\n")
    
    #step 2

    classification = classifier.invoke({"rewritten_input": rewritten})
    print(f" Step 2 - Category: {classification['category']} (confidence: {classification['confidence']})")

    #step3
    final = responder.invoke({
        "original_input": raw_input,
        "rewritten_input": rewritten,
        "category": classification["category"]
    })
    print(f"Step 3 - Priority: {final.get('priority', 'N/A')}, Escalate: {final.get('escalate_to_human', 'N/A')}\nResponse:\n{final.get('response_message', 'N/A')}")

if __name__ == "__main__":
    test_input = "How do i change my password "
    final = run_pipeline(test_input)
    print(final)

# the rewriter file is made to write the prompt of user into structured one prompt
# if user gives the rough prompt it will change it into structured one
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

#initializing variables
load_dotenv() #imports the Gemini API KEY
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature = 0) #temp 0 will give deterministic answer with no fluff

#Following rewritten prompt will enhance the user prompt into a structured one prompt
rewrite_prompt = ChatPromptTemplate.from_template("""
                You are a professional text editor.
                Rewrite the following user input to be clear, formal, and grammatically correct.
                Return ONLY the rewritten text, nothing else.    
                User input: {raw_input}""")

# here we are using the pipeline operator | which takes output of first one and gives it as input of second one
#  and gives output of second one into input of third one
rewriter_chain = rewrite_prompt | llm | StrOutputParser()

if __name__== "__main__":
    result = rewriter_chain.invoke({"raw_input":"plz help i cant login to my acc its broken"})
    print("Rewritten prompt: ",result)


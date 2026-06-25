import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from mem0 import Memory
from mem_config import local_mem0_config

load_dotenv()
print("System working successfully!!")
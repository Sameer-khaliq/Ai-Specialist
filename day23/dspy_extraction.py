import os
import dspy
lm = dspy.LM("groq/llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
dspy.configure(lm=lm)
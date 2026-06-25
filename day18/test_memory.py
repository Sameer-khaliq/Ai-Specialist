import time
from memory_agent import unified_chat, ENTITY_FILE

print("=== RUNNING SESSION 1 ===")
print("Teaching the agent persistent details...")

ans1 = unified_chat("Hey buddy, remember that my favorite stack is FastAPI + LangGraph, and my dog's name is Max.")
print(f"Agent: {ans1}\n")

ans2 = unified_chat("What did I say my dog's name was?")
print(f"Agent: {ans2} (Retrieved from RAM buffer)\n")

print("!!! CRASHING PYTHON PROCESS NOW !!!")
print("Wiping out short_term_history list completely...")
time.sleep(1)

# ----------------------------------------------------
# Simulation of completely restarting Python
# ----------------------------------------------------

print("\n=== RUNNING SESSION 2 (Fresh Run, No RAM) ===")
import memory_agent
memory_agent.short_term_history = [] # Explicitly force-wipe the short term memory array

ans3 = memory_agent.unified_chat("What is my favorite tech stack?")
print(f"Agent: {ans3} (Retrieved from mem0/Entities)\n")

ans4 = memory_agent.unified_chat("Can you remind me of my pet's name?")
print(f"Agent: {ans4} (Retrieved from mem0/Entities)\n")
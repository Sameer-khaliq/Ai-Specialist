import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

print("Loading environment variables from .env file...")
load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[list, add_messages]

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature = 0.7
)

SYSTEM_PROMPT = """Tum ek helpful assistant ho jo conversations yaad rakhta hai.
Hamesha Hinglish ya Urdu/English mix mein jawab do based on user ke message ki language."""


def call_llm(state: AgentState)-> dict:
        
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages_with_system)
    print(f"Trace of response: {response.content[:50]}.....")

    return{'messages': [response]}

#___Graph Construction____
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)


#____Working of agent____

def run_agent():
    with SqliteSaver.from_conn_string("day16/memory.db") as saver:
        app = graph.compile(checkpointer=saver)
        thread_id = input("Thread ID do (default: 'sameer-1'): ").strip() or "sameer-1"
        config = {"configurable": {"thread_id": thread_id}}

        print(f"\n[Agent Started] Thread: {thread_id}")
        print("Type 'exit' to quit, 'history' to see database snapshots\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                print("Session saved to SQLite table. Allah Hafiz!")
                break

            if user_input.lower() == "history":
                # Hum current state ka snapshot database se live dekh sakte hain
                state_snapshot = app.get_state(config)
                if state_snapshot and state_snapshot.values:
                    msgs = state_snapshot.values.get("messages", [])
                    print(f"\n--- History Snapshot ({len(msgs)} messages) ---")
                    for m in msgs:
                        role = "You" if isinstance(m, HumanMessage) else "Agent"
                        print(f"  {role}: {m.content}")
                else:
                    print("[Memory Empty]")
                continue

            if not user_input:
                continue

            # Naya message bhejo. Purani history LangGraph khud thread_id se DB se load karega!
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )

            # Aakhri message print karo
            last_msg = result["messages"][-1]
            print(f"Agent: {last_msg.content}\n")

if __name__ == "__main__":
    run_agent()
import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

def call_llm(state: AgentState) -> dict:
    sys = [SystemMessage(content="You are a helpful assistant with persistent memory.")]
    response = llm.invoke(sys + state["messages"])
    return {"messages": [response]}

g = StateGraph(AgentState)
g.add_node("llm", call_llm)
g.add_edge(START, "llm")
g.add_edge("llm", END)

THREAD = "persistence-automated-test"  

with SqliteSaver.from_conn_string("memory.db") as saver:
    app = g.compile(checkpointer=saver)
    cfg = {"configurable": {"thread_id": THREAD}}

    snap = app.get_state(cfg)
    if snap and snap.values:
        msg_count = len(snap.values.get("messages", []))
        print(f"[DB CHECK]: Existing session found. Messages in memory: {msg_count}")
    else:
        print("[DB CHECK]: New session. No prior memory.")

    convos = [
        "Hi! My name is Sameer and I'm an AI engineer from Gujrat Pakistan.",
        "I'm currently on Day 16 of my 80-day AI specialist roadmap.",
        "What do you remember about me?"
    ]

    for user_msg in convos:
        print(f"You: {user_msg}")
        result = app.invoke(
            {"messages": [HumanMessage(content=user_msg)]},
            config=cfg
        )
        print(f"Agent: {result['messages'][-1].content}\n")
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# ---- 1. STATE DEFINITION ----
class State(TypedDict):
    messages: list[str]
    visit_count: int

# ---- 2. NODE ----
def counter_node(state: State) -> dict:
    # State se purani count uthao, agar pehli baar hai toh default 0 lo
    current_count = state.get("visit_count", 0)
    new_count = current_count + 1
    
    print(f"\n[Counter Node]: Yeh is thread ke liye invoke number {new_count} hai.")
    return {
        "visit_count": new_count,
        "messages": state["messages"] + [f"Visit #{new_count}"]
    }

# ---- 3. GRAPH CONSTRUCTION ----
graph = StateGraph(State)
graph.add_node("counter", counter_node)
graph.add_edge(START, "counter")
graph.add_edge("counter", END)

# ---- 4. COMPILE WITH CHECKPOINTER ----
# 'test_memory.db' naam ki file auto-create hogi workspace mein
with SqliteSaver.from_conn_string("day16/test_memory.db") as saver:
    app = graph.compile(checkpointer=saver)

    # Do alag threads (sessions) define karte hain
    cfg_a = {"configurable": {"thread_id": "thread-A"}}
    cfg_b = {"configurable": {"thread_id": "thread-B"}}

    print("=== PHASE 1: Thread A, Pehli Baar ===")
    r = app.invoke({"messages": [], "visit_count": 0}, config=cfg_a)
    print(f"Thread A state now: {r}")

    print("\n=== PHASE 2: Thread A, Doosri Baar ===")
    # Note: Hum initial state mein  0 bhej rahe hain, 
    # par LangGraph ise ignore karke DB se load karega!
    r = app.invoke({}, config=cfg_a)
    print(f"Thread A state now: {r}")

    print("\n=== PHASE 3: Thread B, Fresh Session ===")
    # Thread B bilkul alag rasta track karega
    r = app.invoke({"messages": [], "visit_count": 0}, config=cfg_b)
    print(f"Thread B state now: {r}")
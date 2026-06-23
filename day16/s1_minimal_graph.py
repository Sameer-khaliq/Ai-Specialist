from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: list[str]
    count : int

def node_a(state : State) -> dict:
    print(f"Node a chal raha hai , count: {state['count']}")

    return { 'count': state['count']+ 1, 'messages':state['messages'] + [' node a se kuch kuch huva']}

def node_b(state: State)-> dict:
    print(f"Node B chal raha hai, count: {state['count']}")
    return {"messages": state["messages"] + [f"Node B done, final count: {state['count']}"]}

graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)
app = graph.compile()

result = app.invoke({'messages':[], 'count': 0})
print("\n--------Result----------")
print(result)

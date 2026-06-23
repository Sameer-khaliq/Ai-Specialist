from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: list[str]
    should_use_tool: bool
    tool_result: str


#______Nodes_______#
def fake_llm(state: State)-> dict:
    #fake llm just for decision making
    last_msg = state['messages'][-1]
    print(f"User bola hai g: {last_msg}")
    if "search" in last_msg.lower():
        return {'should_use_tool' : True} 
    else:
        return {'should_use_tool': False}
    
def fake_tool(state: State)-> dict:
    print("Tool Node: Searching database.....")
    return{
        'tool_result': "Search result: Pakistan population is around 240M",
        "messages": state["messages"] + ["Tool result mil gaya"]
    }

def final_response(state: State)->dict:
    if state.get('tool_result'):
        msg = f"Final response with tool result: {state['tool_result']}"
    else:
        msg = "Final answer: Tool k beghair normal answer de rhaa hoon.."
    return {'messages': state['messages'] + [msg]}



# ______conditional router function________
def route_after_llm(state: State)-> str:
    if state['should_use_tool']:
        return "go_to_tool"
    else:
        return "go_to_direct"


#________graph construction___________
graph = StateGraph(State)


#__Add nodes____
graph.add_node('llm', fake_llm)
graph.add_node('tool', fake_tool)
graph.add_node('respond', final_response)

# ___edges___
graph.add_edge(START, 'llm')
graph.add_conditional_edges(
    'llm',
    route_after_llm,
    {
        'go_to_tool': 'tool',
        'go_to_direct': 'respond'
    }
)

graph.add_edge('tool','respond')
graph.add_edge('respond', END)

app = graph.compile()

print("===  TEST CASE 1: Beghair Tool Ke ===")
r1 = app.invoke({"messages": ["Hello, kya haal hai?"], "should_use_tool": False, "tool_result": ""})
print(f"Final History: {r1['messages']}\n")

print("===  TEST CASE 2: Tool Ke saath ===")
r2 = app.invoke({"messages": ["Please search Pakistan population"], "should_use_tool": False, "tool_result": ""})
print(f"Final History: {r2['messages']}\n")

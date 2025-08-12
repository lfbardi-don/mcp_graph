from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

def build_graph(model, tools):
    model_with_tools = model.bind_tools(tools)
    tool_node = ToolNode(tools)

    def should_call_tool(state: MessagesState):
        last = state["messages"][ -1]
        return "tools" if getattr(last, "tool_calls", None) else END

    async def call_model(state: MessagesState):
        response = await model_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_call_tool)
    builder.add_edge("tools", "call_model")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

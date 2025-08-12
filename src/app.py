import asyncio, os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Any
from mcp_client import get_mcp_tools
from graph_builder import build_graph
from cli import prompt_for_image_request, build_human_message

load_dotenv()

async def main(config: dict[str, Any]):
    model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

    tools = await get_mcp_tools()
    graph = build_graph(model, tools)

    size, style, prompt, system_msg = prompt_for_image_request()
    human_msg = build_human_message(size, style, prompt)

    out = await graph.ainvoke({ "messages": [system_msg, human_msg]}, config=config)
    print(out["messages"][-1].content)

if __name__ == "__main__":
    thread_id = input("\nThread ID:\n\n-> ").strip() or "default"
    config = { "configurable": { "thread_id": thread_id }}
    asyncio.run(main(config))
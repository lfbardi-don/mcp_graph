from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_tools():
    client = MultiServerMCPClient({
        "imagegen": {
            "command": "python",
            "args": ["./tools/mcp_image_server.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    return tools

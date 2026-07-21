import asyncio

from fastmcp import Client

client = Client("http://10.10.16.66:8989/mcp")


async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)


asyncio.run(call_tool("franklin"))

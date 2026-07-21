import asyncio
from fastmcp import Client

client = Client("http://178.62.60.55:8989/mcp")

async def main():
    async with client:

        tools = await client.list_tools()
        print(tools)
        print("\n")

        resources = await client.list_resources()
        print(resources)
        print("\n")

        prompts = await client.list_prompts()
        print(prompts)
        print("\n")

        try:
            result = await client.call_tool("greet", {"name": "franklin"})
            # print(result)
            print("Tool succeeded:", result.data)
        except ToolError as e:
            print(f"Tool failed: {e}")

        try:
             content = await client.read_resource("file://README.md")
             if hasattr(content[0], 'text'):
                 print(content[0].text)

             if hasattr(content[0], 'blob'):
                 print(f"Binary data: {len(content[0].blob)} bytes")

        except Exception as e:
            print(e) 


asyncio.run(main())

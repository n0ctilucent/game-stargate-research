import asyncio

from fastmcp import Client
from fastmcp.exceptions import ToolError  # Fixed: Imported ToolError

client = Client("http://10.10.16.66:8989/mcp")


async def main():
    async with client:

        print("=== Tools ===")
        tools = await client.list_tools()
        print(tools)
        print("\n")

        print("=== Resources ===")
        resources = await client.list_resources()
        print(resources)
        print("\n")

        print("=== Prompts ===")
        prompts = await client.list_prompts()
        print(prompts)
        print("\n")

        print("=== Executing Tool 'greet' ===")
        try:
            result = await client.call_tool("greet", {"name": "franklin"})
            # Accessing response data safely
            print("Tool succeeded:", getattr(result, "data", result))
        except ToolError as e:
            print(f"Tool failed: {e}")
        except Exception as e:
            print(f"Unexpected error calling tool: {e}")

        print("\n=== Reading Resource 'file://README.md' ===")
        try:
            content = await client.read_resource("file://README.md")

            # Handle list vs single object responses
            items = content if isinstance(content, list) else [content]
            for item in items:
                if hasattr(item, "text") and item.text:
                    print("Text Content:\n", item.text)
                elif hasattr(item, "blob") and item.blob:
                    print(f"Binary data: {len(item.blob)} bytes")
                else:
                    print("Raw Content:", item)

        except Exception as e:
            print(f"Resource fetch failed: {e}")


if __name__ == "__main__":
    # Fixed: Calling main() instead of undefined call_tool()
    asyncio.run(main())

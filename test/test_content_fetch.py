import asyncio
import base64

from fastmcp import Client
from fastmcp.exceptions import ToolError

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
            print("Tool succeeded:", getattr(result, "data", result))
        except ToolError as e:
            print(f"Tool failed: {e}")
        except Exception as e:
            print(f"Unexpected error calling tool: {e}")

        print("\n=== Reading Resource 'file://README.md' ===")
        try:
            content = await client.read_resource("file://README.md")

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

        print("\n=== Reading Resource 'file://dreamland.pdf' ===")
        try:
            # Request the PDF resource
            pdf_content = await client.read_resource("file://dreamland.pdf")

            items = pdf_content if isinstance(pdf_content, list) else [pdf_content]
            for item in items:
                if hasattr(item, "blob") and item.blob:
                    # MCP returns binary data as a base64 encoded blob
                    raw_bytes = base64.b64decode(item.blob) if isinstance(item.blob, str) else item.blob
                    
                    print(f"Successfully pulled PDF! Binary data size: {len(raw_bytes)} bytes")
                    
                    # Save it to disk to verify it's the full, valid PDF
                    output_file = "pulled_dreamland.pdf"
                    with open(output_file, "wb") as f:
                        f.write(raw_bytes)
                    print(f"Saved the pulled PDF locally as '{output_file}'")
                    
                elif hasattr(item, "text") and item.text:
                    print("Warning: Received text instead of binary blob. Length:", len(item.text))
                else:
                    print("Raw Content:", item)
        except Exception as e:
            print(f"Resource fetch failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
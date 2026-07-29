import asyncio
from fastmcp import Client
from fastmcp.exceptions import ToolError

# Connection endpoint for the blowfish MariaDB MCP server
SERVER_URL = "http://blowfish.lab.bitsmasher.net:8989/mcp"
client = Client(SERVER_URL)

async def main():
    print(f"Connecting to MCP Server at {SERVER_URL}...\n")
    
    async with client:

        # 1. Discover Capabilities
        print("=== Available Tools ===")
        tools = await client.list_tools()
        print(tools)
        print("\n")

        print("=== Available Resources ===")
        resources = await client.list_resources()
        print(resources)
        print("\n")

        print("=== Available Prompts ===")
        prompts = await client.list_prompts()
        print(prompts)
        print("\n")

        # 2. Test SQL Version Query
        print("=== Executing Tool 'run_sql_query' (SELECT VERSION()) ===")
        try:
            sql_version_query = "SELECT VERSION() as version;"
            result = await client.call_tool("run_sql_query", {"query": sql_version_query})
            data = getattr(result, "data", result)
            print("Tool succeeded:", data)
        except ToolError as e:
            print(f"Tool failed with ToolError: {e}")
        except Exception as e:
            print(f"Unexpected error executing query: {e}")
            
        print("\n")

        # 3. Test Show Tables Query
        print("=== Executing Tool 'run_sql_query' (SHOW TABLES) ===")
        try:
            tables_query = "SHOW TABLES;"
            result = await client.call_tool("run_sql_query", {"query": tables_query})
            data = getattr(result, "data", result)
            print("Tool succeeded:", data)
        except ToolError as e:
            print(f"Tool failed with ToolError: {e}")
        except Exception as e:
            print(f"Unexpected error executing query: {e}")

        print("\n")

        # 4. Optional: Test Table Schema Inspection
        # Replace 'your_table_name' with an actual table name from your MariaDB database
        target_table = "users"  
        print(f"=== Executing Tool 'get_table_schema' for table '{target_table}' ===")
        try:
            result = await client.call_tool("get_table_schema", {"table_name": target_table})
            data = getattr(result, "data", result)
            print("Tool succeeded:", data)
        except ToolError as e:
            print(f"Tool failed with ToolError: {e}")
        except Exception as e:
            print(f"Unexpected error fetching schema: {e}")

if __name__ == "__main__":
    asyncio.run(main())

from fastmcp import FastMCP

mcp = FastMCP("stargate")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="http", host="10.10.16.66", port=8989)

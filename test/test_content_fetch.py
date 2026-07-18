import asyncio
from mcp.client import FastMCPClient   # adjust import for your client library

async def main():
    client = FastMCPClient(
        "stargate",
        transport="tcp",
        host="192.168.1.12",   # IP of the machine running the server
        port=8989,
        token="my-super-secret-token"
    )
    await client.connect()

    # 1️⃣ Fixed‑name version (no argument)
    ctx = await client.call_resource("resource://context")
    print("--- context.md ------------------------------------------------")
    print(ctx)

    # 2️⃣ Variable‑name version (pass filename as a parameter)
    readme = await client.call_resource(
        "resource://context",
        args={"filename": "readme.md"}   # optional, defaults to context.md
    )
    print("--- readme.md -------------------------------------------------")
    print(readme)

    await client.close()

asyncio.run(main())

"""FastMCP server for stargate.research.bitsmasher.net.

Exposes tools and resources for the Dreamland research project,
including documentation listing, database queries against blowfish's MariaDB,
and access to the Dreamland manual PDF."""

import os
import pathlib
import json
from fastmcp import FastMCP

# Resolve paths relative to this file's directory regardless of CWD
_BASE_DIR = pathlib.Path(__file__).resolve().parent
_DOCS_DIR = _BASE_DIR / "docs"
_README_PATH = _DOCS_DIR / "README.md"
_DREAMLAND_PDF = _DOCS_DIR / "minecraft" / "dreamland.pdf"

mcp = FastMCP("research.bitsmasher.net")


# --- Environment helpers for database connections ---

def _db_connect(database=None):
    """Connect to MariaDB on blowfish using environment variables."""
    import mysql.connector  # deferred import
    password = os.getenv("MARIADB_PASSWORD", "")
    return mysql.connector.connect(
        host=os.getenv("MARIADB_HOST", "10.10.12.15"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER", ""),
        password=password,
        database=database or os.getenv("MARIADB_DATABASE", "bluemap"),
    )


def _db_connect_raw():
    """Connect without selecting a database (for SCHEMA queries)."""
    import mysql.connector
    password = os.getenv("MARIADB_PASSWORD", "")
    return mysql.connector.connect(
        host=os.getenv("MARIADB_HOST", "10.10.12.15"),
        port=int(os.getenv("MARIADB_PORT", 3306)),
        user=os.getenv("MARIADB_USER", ""),
        password=password,
    )


# --- Tools ---

@mcp.tool
def greet(name: str) -> str:
    """Simple greeting tool."""
    return f"Hello, {name}!"


@mcp.tool
def list_docs() -> str:
    """List all documentation files available on this server.

    Returns JSON array of objects with 'path' and 'size_bytes' keys."""
    docs = []
    for root, _dirs, files in os.walk(_DOCS_DIR):
        for f in files:
            full = pathlib.Path(root) / f
            rel = full.relative_to(_DOCS_DIR)
            size = full.stat().st_size
            docs.append({"path": str(rel), "size_bytes": size})
    return json.dumps(sorted(docs, key=lambda x: x["path"]), indent=2)


@mcp.tool
def list_databases() -> str:
    """List all databases on the remote MariaDB server.

    Returns JSON array of database names."""
    conn = _db_connect_raw()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA ORDER BY SCHEMA_NAME")
        return json.dumps([row[0] for row in cursor.fetchall()])
    finally:
        cursor.close()
        conn.close()


@mcp.tool
def list_tables(database: str) -> str:
    """List all tables in a given database on the remote MariaDB.

    Returns JSON array of table names."""
    conn = _db_connect(database=database)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SHOW TABLES FROM `{database}`")
        return json.dumps([row[0] for row in cursor.fetchall()])
    finally:
        cursor.close()
        conn.close()


@mcp.tool
def query_database(query: str) -> str:
    """Execute a SQL query against the MariaDB on blowfish.

    Args:
        query: SQL query string (returns JSON array of result rows).

    Uses env vars MARIADB_HOST, MARIADB_PORT, MARIADB_USER,
    MARIADB_PASSWORD, MARIADB_DATABASE (same as the database MCP server)."""
    conn = _db_connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return json.dumps(results, default=str)
    finally:
        cursor.close()
        conn.close()


# --- Resources ---

@mcp.resource("file://dreamland.pdf")
def read_dreamland_pdf():
    """Returns the Dreamland Manual PDF content."""
    if not _DREAMLAND_PDF.exists():
        return "Dreamland PDF not found at docs/minecraft/dreamland.pdf"
    return _DREAMLAND_PDF.read_bytes()


@mcp.resource("file://README.md")
def read_readme():
    """Returns the content of this project's README."""
    if not _README_PATH.exists():
        return "README.md not found"
    return _README_PATH.read_text()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8989)

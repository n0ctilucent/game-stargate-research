esearch Portal FastMCP Server

Fast Micro-Controller Protocol (FastMCP) server running on `stargate.research.bitsmasher.net:8989`. 
Acts as the central control plane and MCP bridge for cluster database operations, local documentation retrieval, and cloud training pipelines.

## Exposed Tools

* `greet`: Health check tool that takes a `name` string and returns a greeting.
* `list_docs`: Scans and returns a JSON list of available documentation files and file sizes.
* `list_databases`: Queries the `blowfish` MariaDB server and lists all available schemas.
* `list_tables`: Lists all relational tables for a given database schema on `blowfish`.
* `query_database`: Executes read-only SQL queries against `blowfish` MariaDB and returns JSON result sets.
* `stage_and_train_vertex`: Staging pipeline tool that reads tokenized datasets from `/mnt/clusterfs/staging/`, uploads them to Google Cloud Storage (`gs://`), and dispatches custom fine-tuning jobs to Vertex AI (NVIDIA L4 GPUs).

## Exposed Resources

* `file://README.md`: Returns the content of this project documentation file.
* `file://dreamland.pdf`: Serves the binary content of the Dreamland Manual PDF located at `docs/minecraft/dreamland.pdf`.

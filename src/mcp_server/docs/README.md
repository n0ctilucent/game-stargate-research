# ollama

`cat notes.txt | ollama run deepseek-r1:latest "do the thing"`

```sh
npm install nostr-tools
curl -fsSL https://openclaw.ai/install.sh | bash
```

## openclaw

- Run regularly                                                                             │
  - `openclaw security audit --deep`                                                            │
  - `openclaw security audit --fix`

## Confirm server is listening

- Check local listen port (default 11434): sudo ss -ltnp | grep -E ':(11434|40001)|ollama'
- Confirm /api/status responds: curl -sS http://127.0.0.1:11434/api/status | jq .

## models

- High-performance general assistant `ollama pull gemma3`
- Top-tier for DevSecOps and Python scripts `ollama pull qwen3.6-coder:14b`
- The current king of logic and chain-of-thought `ollama pull deepseek-r1:14b`

## opencode

OpenCode includes free models, to start:

```sh
curl -fsSL https://opencode.ai/install | bash
ollama launch opencode
cd <project>  # Open directory 
opencode      # Run command
```

For more information visit [https://opencode.ai/docs](https://opencode.ai/docs)

## openclaw

OpenClaw is a personal AI assistant that runs on your own devices. It bridges messaging services (WhatsApp, Telegram, Slack, Discord, iMessage, and more) to AI coding agents through a centralized gateway.

```sh
ollama pull qwen3.6-coder:14b
ollama pull deepseek-r1:14b
OLLAMA_CONTEXT_LENGTH=64000 ollama launch openclaw
```
# Security policy

## Secrets

Never commit API keys, tokens, passwords, cookies, private prompts, or exported
user memories. Use environment variables and a local `.env` file.

The repository ignores `.env`, local data directories, and JSONL memory files.
The committed `.env.example` contains names only, never real values.

## Reporting

For now, report security issues privately to the repository owner. Do not open a
public issue containing credentials or personal memory data.

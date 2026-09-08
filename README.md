# AiMemory

AiMemory is an experimental, privacy-conscious memory and evidence layer for AI-agent workflows.

The project starts from a Windows/OpenCode/Python setup and is designed to work with `open-mem` and `true-mem`. Its goal is to preserve useful context across agents without losing provenance, confidence, or security boundaries.

## Design goals

- Structured memory records instead of untraceable prompt fragments
- Evidence-first hand-offs between research, orchestration, and synthesis
- A systematic cross-check pass for critical claims
- Selective parallel research where independent verification matters
- Static, role-based model routing
- No secrets or API keys in the repository

## Planned roles

- **main** — orchestration, routing, analysis, and synthesis
- **recherche** — source collection and structured evidence output
- **cross-check** — independent verification and conflict detection
- **critic** — optional second-model read-through for decision reports

## Status

Initial repository scaffold. Interfaces and schemas are deliberately small so the project can evolve without locking into one memory backend too early.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

Copy `.env.example` to `.env` and add local credentials there. Never commit `.env`.

## Repository map

- `src/aimemory/` — core Python package
- `tests/` — automated tests
- `docs/` — architecture and schemas
- `agents/` — role definitions
- `config/` — safe example configuration

## License

No license has been selected yet. Until one is added, all rights are reserved.

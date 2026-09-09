# Architecture

## Direction: Variant C (Hybrid)

AiMemory extends the existing OpenCode setup without multiplying the permanent
agent count. The main agent remains responsible for orchestration, routing,
analysis, and synthesis.

1. A role receives a bounded task.
2. Research produces structured evidence records.
3. Memory stores content together with source, confidence, and verification state.
4. Cross-check independently tests critical claims and records conflicts.
5. Main synthesizes only after reviewing evidence and cross-check results.
6. Decision reports may receive an optional second-model critic read-through.

## Components

- `MemoryRecord`: durable content plus tags, metadata, and evidence
- `Evidence`: claim, source, optional excerpt, confidence, and status
- `JsonlMemoryStore`: local development backend
- `SQLiteMemoryStore`: atomic local storage and project namespaces
- `adapters.open_mem`: upstream v1 export snapshot import
- `adapters.true_mem`: read-only SQLite snapshot import
- CLI: explicit local capture, search, context, import/export and diagnosis

## Model routing

Routing is static and role-based:

- DeepSeek Flash: default workload
- Gemini: complex reasoning and critique
- Groq: fast, structured tasks
- Additional providers only on explicit selection; no automatic model fallback

Model names and credentials belong in local configuration, never committed files.

AiMemory does not execute models. Role routing describes the host workflow only. See [integrations](integrations.md) for tested source contracts and live-integration limitations.

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

## Initial components

- `MemoryRecord`: durable content plus tags, metadata, and evidence
- `Evidence`: claim, source, optional excerpt, confidence, and status
- `JsonlMemoryStore`: local development backend
- Future adapters: `open-mem`, `true-mem`, or a database

## Model routing

Routing is static and role-based:

- DeepSeek Flash: default workload
- Gemini: complex reasoning and critique
- Groq: fast, structured tasks
- Orca/OpenRouter: reserve or fallback

Model names and credentials belong in local configuration, never committed files.

# Evidence schema

Every important factual hand-off should preserve enough information for another
agent to verify it.

```json
{
  "claim": "A concise, falsifiable statement",
  "source": "URL, file reference, or stable identifier",
  "excerpt": "Optional short supporting passage",
  "confidence": 0.8,
  "status": "unverified"
}
```

## Rules

- `claim` must be specific enough to confirm or reject.
- `source` must identify where the support came from.
- `excerpt` is optional and should remain short.
- `confidence` ranges from `0.0` to `1.0`.
- `status` is one of `unverified`, `supported`, `disputed`, or `rejected`.
- Conflicting evidence is retained and marked; it is not silently overwritten.

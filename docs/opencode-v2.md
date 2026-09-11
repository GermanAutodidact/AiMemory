# OpenCode V2 beta

V1 and V2 use different plugin APIs. Both adapters are shipped; choose one for
each plugin directory. Do not load the V1 and V2 implementations together in the
same host. Both use the same Python backend, database format and namespaces.

## Windows

From the repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1 -OpenCodeApi v2
```

For V1 select `-OpenCodeApi v1`. Only the AiMemory-managed plugin is replaced.
Existing memory is retained. For separate parallel installations use different
project/config directories and install the appropriate adapter in each.

Manual project installation: `python -m aimemory install-opencode PROJECT --api v2 --update`.
Global installation: `python -m aimemory install-opencode --global --api v2 --update`.

Restart the V2 background server after installation, or open a fresh terminal and
start `opencode2 --standalone` to test without reusing the background service.
Send `#merken: Mein AiMemory-Testcode ist BERLIN-4711.`. Then verify with:

```powershell
& "$HOME\AiMemory\.venv\Scripts\python.exe" -m aimemory --db "$env:LOCALAPPDATA\AiMemory\memory.sqlite3" --namespace global search "BERLIN-4711"
```

Finally ask for the test code in a new session. A model confirmation alone is not
proof of storage. Captures are explicit, not automatic recording of all chats.

## Contract and verification limits

Implementation checked on 2026-09-11 against the upstream `v2` branch:

- [Plugin object and setup](https://github.com/anomalyco/opencode/blob/v2/packages/plugin/src/promise/plugin.ts)
- [Session prompt, context and compaction](https://github.com/anomalyco/opencode/blob/v2/packages/plugin/src/promise/session.ts)
- [Registration and disposal](https://github.com/anomalyco/opencode/blob/v2/packages/plugin/src/promise/registration.ts)
- [Prompt text schema](https://github.com/anomalyco/opencode/blob/v2/packages/schema/src/prompt-input.ts)

The adapter exports an object with `id` and `setup`; `Plugin.define` in this API
is an identity helper, so no separate SDK dependency is installed. It registers
`session.hook("prompt", ...)`, `context` and `compaction`. Context memories are
untrusted user-channel reference data, not system instructions. Python calls
use stdin, no shell interpolation, a 10-second timeout and generic errors.
Activation checks Python/database access; failed writes never create success receipts.

`node --test tests/opencode-v2.test.mjs` uses a simulated V2 registration host
with real Python and SQLite. It is NOT a test inside OpenCode itself. The exact
Windows beta build `0.0.0-beta-18985` has not yet been runtime-verified; the upstream
branch can differ from that build. No compatibility with every future beta is claimed.

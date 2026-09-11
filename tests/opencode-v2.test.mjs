import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import Plugin from "../src/aimemory/opencode/aimemory-v2.js";

test("V2 prompt captures through Python, new context and compaction retrieve, cleanup disposes", async () => {
  const temp = mkdtempSync(join(tmpdir(), "aimemory-v2-"));
  const old = { ...process.env };
  process.env.AIMEMORY_DB = join(temp, "memory.sqlite3");
  delete process.env.AIMEMORY_NAMESPACE;
  const hooks = new Map();
  const setup = (directory) => Plugin.setup({ location: { directory }, session: {
    hook: async (name, callback) => {
      hooks.set(name, callback);
      return { dispose: async () => hooks.delete(name) };
    },
  } });
  try {
    const cleanup = await setup(join(temp, "project"));
    assert.deepEqual([...hooks.keys()], ["prompt", "context", "compaction"]);
    await hooks.get("prompt")({ sessionID: "s1", messageID: "m1",
      prompt: { text: "#merken: BERLIN-4711; $(not-a-command)" } });
    const current = { sessionID: "s1", system: [], messages: [] };
    await hooks.get("context")(current);
    assert.match(current.system[0].text, /erfolgreich/);
    assert.match(current.messages[0].content[0].text, /BERLIN-4711/);
    await cleanup();
    assert.equal(hooks.size, 0);
    const cleanup2 = await setup(join(temp, "project"));
    for (const name of ["context", "compaction"]) {
      const input = { sessionID: "s2", system: [], messages: [] };
      await hooks.get(name)(input);
      assert.match(input.messages[0].content[0].text, /BERLIN-4711/);
      assert.equal(input.system.length, 0);
    }
    await hooks.get("prompt")({ sessionID: "s2", messageID: "m2", prompt: { text: "ordinary chat" } });
    await cleanup2();
    const cleanup3 = await setup(join(temp, "other"));
    const isolated = { sessionID: "s3", system: [], messages: [] };
    await hooks.get("context")(isolated);
    assert.equal(isolated.messages.length, 0);
    await cleanup3();
    process.env.AIMEMORY_PYTHON = join(temp, "nonexistent-python");
    await assert.rejects(setup(join(temp, "project")), /operation failed/);
    assert.equal(hooks.size, 0);
  } finally {
    for (const key of ["AIMEMORY_DB", "AIMEMORY_NAMESPACE", "AIMEMORY_PYTHON"]) {
      if (old[key] === undefined) delete process.env[key]; else process.env[key] = old[key];
    }
    rmSync(temp, { recursive: true, force: true });
  }
});

test("V2 rejects a V1 host instead of pretending to load", async () => {
  await assert.rejects(Plugin.setup({ directory: "/demo" }), /session.hook/);
});

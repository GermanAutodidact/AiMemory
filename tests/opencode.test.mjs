import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { AiMemoryPlugin as Plugin } from "../src/aimemory/opencode/aimemory.js";

test("real Python bridge captures once, injects next session and compaction, isolates projects", async () => {
  const temp = mkdtempSync(join(tmpdir(), "aimemory-test-"));
  const oldDB = process.env.AIMEMORY_DB;
  const oldNamespace = process.env.AIMEMORY_NAMESPACE;
  process.env.AIMEMORY_DB = join(temp, "memory.db");
  delete process.env.AIMEMORY_NAMESPACE;
  try {
    const warnings = [];
    const client = {app: {log: async x => warnings.push(x)}};
    const host = await Plugin({directory: join(temp, "a"), client});
    const output = {message: {role: "user", id: "m1", time: {created: 1788912000000}},
      parts: [{type: "text", text: "#merken: Deutsch; $(echo NOT_EXECUTED)"}]};
    await host["chat.message"]({sessionID: "s1"}, output);
    await host["chat.message"]({sessionID: "s1"}, output);
    const next = await Plugin({directory: join(temp, "a"), client});
    const system = {system: []};
    await next["experimental.chat.system.transform"]({sessionID: "s2"}, system);
    assert.equal(system.system.length, 2);
    assert.match(system.system[0], /Briefly confirm that it was saved/);
    const lines = system.system[1].split("\n").slice(1);
    assert.equal(lines.length, 1);
    assert.equal(JSON.parse(lines[0]).content, "Deutsch; $(echo NOT_EXECUTED)");
    const compact = {context: ["existing"]};
    await next["experimental.session.compacting"]({}, compact);
    assert.equal(compact.context.length, 2);
    const other = await Plugin({directory: join(temp, "b"), client});
    const isolated = {system: []};
    await other["experimental.chat.system.transform"]({}, isolated);
    assert.equal(isolated.system.length, 1);
    assert.match(isolated.system[0], /#merken:/);
    for (const parts of [[{type: "text", text: "ordinary private conversation"}],
                          [{type: "text", text: "#merken: synthetic", synthetic: true}]]) {
      await host["chat.message"]({sessionID: "s1"}, {...output, parts});
    }
    await host["chat.message"]({sessionID: "s1"}, {...output, message: {...output.message, role: "assistant"}});
    const after = {system: []};
    await host["experimental.chat.system.transform"]({}, after);
    assert.equal(after.system[1], system.system[1]);
    assert.equal(warnings.length, 0);
  } finally {
    if (oldDB === undefined) delete process.env.AIMEMORY_DB; else process.env.AIMEMORY_DB = oldDB;
    if (oldNamespace === undefined) delete process.env.AIMEMORY_NAMESPACE; else process.env.AIMEMORY_NAMESPACE = oldNamespace;
    rmSync(temp, {recursive: true, force: true});
  }
});

test("missing Python logs generic failure and preserves host context", async () => {
  const old = process.env.AIMEMORY_PYTHON;
  process.env.AIMEMORY_PYTHON = "/nonexistent/aimemory-python";
  try {
    const warnings = [];
    const host = await Plugin({directory: "/demo", client: {app: {log: async x => warnings.push(x)}}});
    const output = {system: ["existing"]};
    await host["experimental.chat.system.transform"]({}, output);
    assert.equal(output.system.length, 2);
    assert.equal(output.system[0], "existing");
    assert.match(output.system[1], /#remember:/);
    assert.equal(warnings.length, 1);
    assert.equal(warnings[0].body.level, "warn");
  } finally {
    if (old === undefined) delete process.env.AIMEMORY_PYTHON; else process.env.AIMEMORY_PYTHON = old;
  }
});

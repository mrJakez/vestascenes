const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const test = require("node:test");
const decode = require("decode-uri-component");

test("decodes UTF-8 and preserves query-string's CommonJS API", () => {
  const queryString = require("query-string");
  assert.equal(decode("Gr%C3%BC%C3%9Fe%20%E2%82%AC"), "Grüße €");
  const parsed = queryString.parse("scene=SnapshotScene&title=Gr%C3%BC%C3%9Fe+Welt");
  assert.equal(parsed.scene, "SnapshotScene");
  assert.equal(parsed.title, "Grüße Welt");
  assert.equal(queryString.stringify({ scene: "SnapshotScene" }), "scene=SnapshotScene");
});

test("tolerates malformed escapes and rejects non-string inputs", () => {
  assert.equal(decode("%FF%41%"), "%FFA%");
  assert.throws(() => decode(null), TypeError);
});

test("malformed percent-encoded input finishes within the regression deadline", () => {
  const result = spawnSync(process.execPath, ["-e", `
    const assert = require('node:assert/strict');
    const decode = require('decode-uri-component');
    const input = '%FF'.repeat(10000);
    assert.equal(decode(input), input);
  `], { cwd: require("node:path").resolve(__dirname, ".."), timeout: 3000 });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr.toString());
});

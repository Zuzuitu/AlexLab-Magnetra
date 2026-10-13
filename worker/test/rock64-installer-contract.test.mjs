import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

for (const filename of ["install-btdigg.sh", "update-btdigg.sh"]) {
 test(filename + " does not create root-owned Python bytecode inside runner checkout", () => {
  const source = readFileSync(new URL("../../rock64/"+filename, import.meta.url), "utf8");
  assert.match(source, /python3 -B -m unittest discover/);
  assert.match(source, /ast\.parse\(/);
  assert.doesNotMatch(source, /python3 -m py_compile/);
  assert.match(source, /set -Ee?uo pipefail/);
 });
}

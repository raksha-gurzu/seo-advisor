import { Graphviz } from "@hpcc-js/wasm-graphviz";
import { readFileSync, writeFileSync } from "fs";
const gv = await Graphviz.load();
for (const f of process.argv.slice(2)) { writeFileSync(f.replace(/\.dot$/, ".svg"), gv.dot(readFileSync(f, "utf8"), "svg")); console.log("ok", f); }

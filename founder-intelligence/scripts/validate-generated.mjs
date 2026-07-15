import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const APP_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const generated = join(APP_ROOT, "src", "generated");
const knowledge = JSON.parse(readFileSync(join(generated, "knowledge-index.json"), "utf8"));
const dashboard = JSON.parse(readFileSync(join(generated, "dashboard-data.json"), "utf8"));
const serializedGeneratedData = JSON.stringify({ knowledge, dashboard });
const issues = [];

function require(condition, message) {
  if (!condition) issues.push(message);
}

require(knowledge.contractVersion === 1, "knowledge contract version must be 1");
require(knowledge.method === "deterministic-local-tfidf-sparse-v1", "unexpected vectorization method");
require(knowledge.sourceFiles >= 80, "expected at least 80 admitted source files");
require(Array.isArray(knowledge.files), "knowledge file manifest is missing");
require(knowledge.files.length === knowledge.sourceFiles, "knowledge file manifest count drifted");
require(knowledge.files.every((file) => file.path && file.title && file.layer), "knowledge file manifest is incomplete");
require(knowledge.chunks.length >= 300, "expected at least 300 knowledge chunks");
require(knowledge.vocabulary.length >= 500, "expected at least 500 vector terms");
require(knowledge.chunks.every((chunk) => chunk.id && chunk.path && chunk.text), "knowledge chunk is incomplete");
require(knowledge.chunks.every((chunk) => !chunk.path.startsWith("website/")), "website content entered the knowledge corpus");
require(knowledge.chunks.every((chunk) => !/-----BEGIN .*PRIVATE KEY-----/.test(chunk.text)), "private key marker found");
require(!/\/Users\//.test(serializedGeneratedData), "local macOS path entered generated data");
require(!/(?:\/home\/|\/tmp\/|\/var\/folders\/)/.test(serializedGeneratedData), "local Unix path entered generated data");
require(!/[A-Za-z]:\\Users\\/i.test(serializedGeneratedData), "local Windows path entered generated data");
require(
  !/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(serializedGeneratedData),
  "email-shaped value entered generated data",
);
require(dashboard.sources.length === 42, "source ledger count must remain 42");
require(dashboard.blockers.length === 12, "blocker count must remain 12");
require(dashboard.blockers.every((row) => row.current_state === "blocked"), "a blocker was silently promoted");
require(dashboard.experiments.length === 8, "experiment count must remain 8");
require(
  dashboard.experiments.filter((row) => !row.execution_state.startsWith("blocked")).map((row) => row.experiment_id).join(",") ===
    "EXP-001,EXP-002,EXP-003",
  "experiment allowlist drifted",
);

if (issues.length) {
  console.error(`FAIL: ${issues.length} generated-data issue(s)`);
  issues.forEach((issue) => console.error(`- ${issue}`));
  process.exit(1);
}

console.log(`PASS: ${knowledge.sourceFiles} files, ${knowledge.chunks.length} chunks, 42 sources, 12 blockers, 8 experiments.`);

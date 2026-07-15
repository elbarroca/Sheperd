import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const APP_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REPO_ROOT = resolve(APP_ROOT, "..");
const GENERATED_ROOT = join(APP_ROOT, "src", "generated");
const KNOWLEDGE_OUTPUT = join(GENERATED_ROOT, "knowledge-index.json");
const DASHBOARD_OUTPUT = join(GENERATED_ROOT, "dashboard-data.json");
const VECTOR_CONTRACT = JSON.parse(readFileSync(join(APP_ROOT, "vector-contract.json"), "utf8"));
const MAX_VOCABULARY = VECTOR_CONTRACT.maxVocabulary;
const MAX_CHUNK_CHARACTERS = VECTOR_CONTRACT.maxChunkCharacters;

const CORPUS_ROOTS = [
  "00_System",
  "01_Company",
  "02_Domain",
  "03_GTM",
  "04_Operations",
  "05_AI",
  "06_Goals",
  "06_Research",
  "07_Founder_Operating_System/data",
  "10_Sources",
  "90_Templates",
  "context",
];

const DASHBOARD_DATASETS = {
  sources: "06_Research/data/source-ledger.csv",
  workflows: "06_Research/data/workflows.csv",
  aiOpportunities: "06_Research/data/ai-opportunities.csv",
  timeSavings: "06_Research/data/time-savings.csv",
  blockers: "07_Founder_Operating_System/data/blockers.csv",
  experiments: "07_Founder_Operating_System/data/experiments.csv",
  measurements: "07_Founder_Operating_System/data/measurements.csv",
  contentBacklog: "07_Founder_Operating_System/data/content_backlog.csv",
  artifacts: "07_Founder_Operating_System/data/artifact_manifest.csv",
};

const STOP_WORDS = new Set(VECTOR_CONTRACT.stopWords);

function normalizePath(path) {
  return path.split("\\").join("/");
}

function walk(root) {
  if (!existsSync(root)) return [];
  const results = [];
  for (const name of readdirSync(root).sort()) {
    const path = join(root, name);
    const stats = statSync(path);
    if (stats.isDirectory()) results.push(...walk(path));
    if (stats.isFile() && [".md", ".csv"].includes(extname(path).toLowerCase())) results.push(path);
  }
  return results;
}

function parseFrontmatter(raw) {
  if (!raw.startsWith("---\n")) return { attributes: {}, body: raw };
  const end = raw.indexOf("\n---\n", 4);
  if (end < 0) return { attributes: {}, body: raw };
  const attributes = {};
  let listKey = null;
  for (const line of raw.slice(4, end).split("\n")) {
    const listMatch = line.match(/^\s+-\s+(.+)$/);
    if (listMatch && listKey) {
      attributes[listKey] = [...(attributes[listKey] ?? []), listMatch[1].trim()];
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    const [, key, value] = match;
    listKey = value ? null : key;
    attributes[key] = value.replace(/^['"]|['"]$/g, "");
  }
  return { attributes, body: raw.slice(end + 5) };
}

function parseCsv(raw) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < raw.length; index += 1) {
    const character = raw[index];
    if (quoted && character === '"' && raw[index + 1] === '"') {
      field += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && raw[index + 1] === "\n") index += 1;
      row.push(field);
      if (row.some((value) => value.trim())) rows.push(row);
      row = [];
      field = "";
    } else {
      field += character;
    }
  }
  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }
  const [headers = [], ...values] = rows;
  return values.map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
}

function redactSensitiveText(text) {
  return text
    .replace(/\/Users\/[^/\s]+(?:\/[^\s|`"')\]]+)*/g, "[local-path]")
    .replace(/(?:\/home\/[^/\s]+|\/tmp|\/var\/folders)(?:\/[^\s|`"')\]]+)*/g, "[local-path]")
    .replace(/[A-Za-z]:\\Users\\[^\\\s]+(?:\\[^\s|`"')\]]+)*/gi, "[local-path]")
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[email-redacted]");
}

function cleanMarkdown(text) {
  return redactSensitiveText(text)
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/!\[\[([^\]]+)\]\]/g, "$1")
    .replace(/\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]/g, (_, target, label) => label || target)
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")
    .replace(/^>\s?\[![^\]]+\].*$/gm, " ")
    .replace(/[|*_`>#~-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function splitLongText(text) {
  if (text.length <= MAX_CHUNK_CHARACTERS) return [text];
  const sentences = text.split(/(?<=[.!?])\s+/);
  const chunks = [];
  let current = "";
  for (const sentence of sentences) {
    if (current && current.length + sentence.length + 1 > MAX_CHUNK_CHARACTERS) {
      chunks.push(current);
      current = sentence;
    } else {
      current = current ? `${current} ${sentence}` : sentence;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

function classifyLayer(path) {
  if (path.startsWith("context/Ricardo")) return "ricardo-interpretation";
  if (path.startsWith("context/")) return "founder-context";
  if (path.startsWith("10_Sources/")) return "source";
  if (path.startsWith("90_Templates/")) return "template";
  if (/^(03_GTM|04_Operations|05_AI|06_Goals)\//.test(path)) return "operating-system";
  if (path.startsWith("07_Founder_Operating_System/")) return "structured-data";
  return "research";
}

function stableId(path, section, index) {
  return createHash("sha256").update(`${path}:${section}:${index}`).digest("hex").slice(0, 16);
}

function markdownChunks(path, raw) {
  const { attributes, body } = parseFrontmatter(raw);
  const title = attributes.title || path.split("/").at(-1).replace(/\.md$/i, "");
  const sections = [];
  let section = "Overview";
  let lines = [];
  const flush = () => {
    const text = cleanMarkdown(lines.join("\n"));
    if (text.length >= 40) sections.push({ section, text });
    lines = [];
  };
  for (const line of body.split("\n")) {
    const heading = line.match(/^#{1,4}\s+(.+)$/);
    if (heading) {
      flush();
      section = cleanMarkdown(heading[1]);
    } else {
      lines.push(line);
    }
  }
  flush();
  const tags = Array.isArray(attributes.tags) ? attributes.tags : [];
  const chunks = [];
  for (const item of sections) {
    splitLongText(item.text).forEach((text, index) => {
      chunks.push({
        id: stableId(path, item.section, index),
        path,
        title,
        section: item.section,
        layer: classifyLayer(path),
        evidenceStatus: attributes.evidence_status || "unknown",
        confidentiality: attributes.confidentiality || "internal",
        tags,
        text,
      });
    });
  }
  return chunks;
}

function csvChunks(path, raw) {
  const rows = parseCsv(raw);
  return rows.map((row, index) => {
    const primary = Object.values(row).find((value) => /^(?:[A-Z]+-\d+|\d+)$/.test(value)) || String(index + 1);
    const text = Object.entries(row)
      .filter(([, value]) => value.trim())
      .map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`)
      .join(". ");
    return {
      id: stableId(path, primary, index),
      path,
      title: path.split("/").at(-1).replace(/\.csv$/i, "").replaceAll("-", " "),
      section: `Record ${primary}`,
      layer: classifyLayer(path),
      evidenceStatus: row.evidence_status || row.current_state || "structured-data",
      confidentiality: "internal",
      tags: [],
      text: redactSensitiveText(text).slice(0, MAX_CHUNK_CHARACTERS),
    };
  });
}

function fileManifest(path, raw) {
  if (extname(path).toLowerCase() === ".md") {
    const { attributes } = parseFrontmatter(raw);
    return {
      path,
      title: attributes.title || path.split("/").at(-1).replace(/\.md$/i, ""),
      layer: classifyLayer(path),
      evidenceStatus: attributes.evidence_status || "unknown",
      confidentiality: attributes.confidentiality || "internal",
      tags: Array.isArray(attributes.tags) ? attributes.tags : [],
    };
  }

  const firstRow = parseCsv(raw)[0] ?? {};
  return {
    path,
    title: path.split("/").at(-1).replace(/\.csv$/i, "").replaceAll("-", " "),
    layer: classifyLayer(path),
    evidenceStatus: firstRow.evidence_status || firstRow.current_state || "structured-data",
    confidentiality: "internal",
    tags: [],
  };
}

function tokenize(text) {
  return (text.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [])
    .filter((term) => term.length > 1 && !STOP_WORDS.has(term));
}

function buildVectors(chunks) {
  const tokenized = chunks.map((chunk) => tokenize(`${chunk.title} ${chunk.section} ${chunk.text}`));
  const documentFrequency = new Map();
  for (const tokens of tokenized) {
    for (const term of new Set(tokens)) documentFrequency.set(term, (documentFrequency.get(term) ?? 0) + 1);
  }
  const vocabulary = [...documentFrequency.entries()]
    .filter(([, count]) => count >= 2)
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, MAX_VOCABULARY)
    .map(([term]) => term);
  const termIndex = new Map(vocabulary.map((term, index) => [term, index]));
  const idf = vocabulary.map((term) => Math.log((1 + chunks.length) / (1 + documentFrequency.get(term))) + 1);
  const vectorized = chunks.map((chunk, chunkIndex) => {
    const counts = new Map();
    for (const term of tokenized[chunkIndex]) {
      const index = termIndex.get(term);
      if (index !== undefined) counts.set(index, (counts.get(index) ?? 0) + 1);
    }
    const weighted = [...counts.entries()].map(([index, count]) => [index, (1 + Math.log(count)) * idf[index]]);
    const magnitude = Math.sqrt(weighted.reduce((sum, [, value]) => sum + value * value, 0)) || 1;
    const vector = weighted
      .map(([index, value]) => [index, Number((value / magnitude).toFixed(6))])
      .sort((left, right) => left[0] - right[0]);
    return { ...chunk, vector };
  });
  return { vocabulary, idf: idf.map((value) => Number(value.toFixed(6))), chunks: vectorized };
}

function latestSourceDate(files) {
  const dates = files.flatMap((file) => {
    const raw = readFileSync(file, "utf8");
    if (extname(file).toLowerCase() === ".md") {
      const { attributes } = parseFrontmatter(raw);
      return [attributes.updated, attributes.checked, attributes.date]
        .filter((value) => typeof value === "string" && /^20\d{2}-\d{2}-\d{2}$/.test(value));
    }
    return parseCsv(raw).flatMap((row) =>
      [row.updated, row.checked, row.checked_at, row.date]
        .filter((value) => typeof value === "string" && /^20\d{2}-\d{2}-\d{2}$/.test(value)),
    );
  });
  return dates.sort().at(-1) ?? "unknown";
}

function readDashboardData() {
  return Object.fromEntries(
    Object.entries(DASHBOARD_DATASETS).map(([key, path]) => [key, parseCsv(readFileSync(join(REPO_ROOT, path), "utf8"))]),
  );
}

function writeJson(path, value) {
  const next = `${JSON.stringify(value, null, 2)}\n`;
  if (existsSync(path) && readFileSync(path, "utf8") === next) return false;
  writeFileSync(path, next, "utf8");
  return true;
}

function reuseCommittedOutputs() {
  if (!existsSync(KNOWLEDGE_OUTPUT) || !existsSync(DASHBOARD_OUTPUT)) {
    throw new Error("Canonical corpus is unavailable and committed generated data is missing");
  }
  JSON.parse(readFileSync(KNOWLEDGE_OUTPUT, "utf8"));
  JSON.parse(readFileSync(DASHBOARD_OUTPUT, "utf8"));
  console.log("Canonical corpus not present; using committed generated dashboard data.");
}

function main() {
  if (!existsSync(join(REPO_ROOT, "00_System"))) {
    reuseCommittedOutputs();
    return;
  }
  const files = CORPUS_ROOTS.flatMap((root) => walk(join(REPO_ROOT, root)));
  const manifests = [];
  const chunks = files.flatMap((file) => {
    const path = normalizePath(relative(REPO_ROOT, file));
    const raw = readFileSync(file, "utf8");
    manifests.push(fileManifest(path, raw));
    return extname(file).toLowerCase() === ".csv" ? csvChunks(path, raw) : markdownChunks(path, raw);
  });
  const vectorData = buildVectors(chunks);
  const sourceDate = latestSourceDate(files);
  const knowledge = {
    contractVersion: 1,
    method: VECTOR_CONTRACT.method,
    boundary: "Public read-only D0/D1 research brief; no customer records or external embedding service",
    sourceDate,
    sourceFiles: files.length,
    files: manifests,
    vocabulary: vectorData.vocabulary,
    idf: vectorData.idf,
    chunks: vectorData.chunks,
  };
  const dashboard = {
    contractVersion: 1,
    sourceDate,
    scores: {
      researchSystem: 9.3,
      gtmDesign: 9.2,
      realMarketEvidence: 1.8,
      safeExecutionReadiness: 3.3,
    },
    ...readDashboardData(),
  };
  mkdirSync(GENERATED_ROOT, { recursive: true });
  const changed = [writeJson(KNOWLEDGE_OUTPUT, knowledge), writeJson(DASHBOARD_OUTPUT, dashboard)].some(Boolean);
  console.log(`${changed ? "Updated" : "Verified"} ${files.length} files, ${chunks.length} chunks, ${vectorData.vocabulary.length} terms.`);
}

main();

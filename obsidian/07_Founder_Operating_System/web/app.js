"use strict";

const scoreLabels = {
  research_system: ["Research system", "Current sources and evidence controls"],
  gtm_system_design: ["GTM system design", "Decision architecture, not market proof"],
  real_market_evidence: ["Real market evidence", "No authorized customer cohort"],
  safe_execution_readiness: ["Safe execution readiness", "Core activation gates remain blocked"],
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function renderScores(scores) {
  const container = document.querySelector("#score-cards");
  clear(container);
  Object.entries(scores).forEach(([key, value]) => {
    const [label, note] = scoreLabels[key] || [key, "Internal planning score"];
    const card = document.createElement("article");
    card.className = "score-card";
    const title = document.createElement("p");
    title.className = "section-label";
    title.textContent = label;
    const score = document.createElement("strong");
    score.className = "score-value";
    score.textContent = `${Number(value).toFixed(1)}/10`;
    const boundary = document.createElement("p");
    boundary.textContent = note;
    card.append(title, score, boundary);
    container.appendChild(card);
  });
}

function rowsToObjects(result) {
  return result.rows.map((row) =>
    Object.fromEntries(result.columns.map((column, index) => [column, row[index]])),
  );
}

function renderBars(targetSelector, result, labelColumn) {
  const target = document.querySelector(targetSelector);
  clear(target);
  const rows = rowsToObjects(result);
  const maximum = Math.max(...rows.map((row) => Number(row.count)), 1);
  rows.forEach((row) => {
    const wrapper = document.createElement("div");
    wrapper.className = "bar-row";
    const label = document.createElement("span");
    label.textContent = String(row[labelColumn]);
    const track = document.createElement("div");
    track.className = "bar-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = `${(Number(row.count) / maximum) * 100}%`;
    track.appendChild(fill);
    const count = document.createElement("strong");
    count.textContent = String(row.count);
    wrapper.append(label, track, count);
    target.appendChild(wrapper);
  });
}

function renderTable(target, result) {
  clear(target);
  if (!result.columns.length) {
    const empty = document.createElement("p");
    empty.textContent = "Query returned no columns.";
    target.appendChild(empty);
    return;
  }
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  result.columns.forEach((column) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = column.replaceAll("_", " ");
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  const tbody = document.createElement("tbody");
  result.rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value === null ? "unknown" : String(value);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.append(thead, tbody);
  target.appendChild(table);
}

async function loadTable(tableName) {
  const preview = await api(`/api/table?name=${encodeURIComponent(tableName)}&limit=50`);
  renderTable(document.querySelector("#table-preview"), preview);
  document.querySelector("#table-meta").textContent =
    `${preview.row_count} rows shown${preview.truncated ? " · result truncated" : ""}`;
}

async function setupTables() {
  const catalog = await api("/api/tables");
  const select = document.querySelector("#table-select");
  catalog.tables.forEach((table) => {
    const option = document.createElement("option");
    option.value = table.name;
    option.textContent = `${table.name} · ${table.columns.length} columns`;
    select.appendChild(option);
  });
  select.value = "blockers";
  select.addEventListener("change", () => loadTable(select.value));
  await loadTable(select.value);
}

async function runQuery() {
  const status = document.querySelector("#query-status");
  const target = document.querySelector("#query-results");
  status.textContent = "Running bounded read-only query…";
  try {
    const result = await api("/api/query", {
      method: "POST",
      body: JSON.stringify({ sql: document.querySelector("#sql-input").value, limit: 100 }),
    });
    renderTable(target, result);
    status.textContent = `${result.row_count} rows returned${result.truncated ? " · truncated" : ""}`;
  } catch (error) {
    clear(target);
    status.textContent = `Blocked: ${error.message}`;
  }
}

function weightValue(selector) {
  return Number(document.querySelector(selector).value) / 100;
}

function renderRanking(result) {
  document.querySelector("#ranking-warning").textContent = result.warning;
  const target = document.querySelector("#ranking-results");
  clear(target);
  result.experiments.forEach((experiment) => {
    const card = document.createElement("article");
    card.className = "rank-card";
    const score = document.createElement("strong");
    score.className = "rank-score";
    score.textContent = experiment.priority_score.toFixed(2);
    const body = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = `${experiment.experiment_id} · ${experiment.name}`;
    const hypothesis = document.createElement("p");
    hypothesis.textContent = experiment.primary_hypothesis;
    body.append(title, hypothesis);
    const badge = document.createElement("span");
    badge.className = `gate-badge${experiment.execution_allowed ? " eligible" : ""}`;
    badge.textContent = experiment.execution_allowed ? "Internal only" : experiment.execution_state;
    card.append(score, body, badge);
    target.appendChild(card);
  });
}

async function rankExperiments(event) {
  if (event) event.preventDefault();
  const weights = {
    learning_value: weightValue("#learning-weight"),
    evidence_readiness: weightValue("#readiness-weight"),
    lower_risk: weightValue("#risk-weight"),
    lower_effort: weightValue("#effort-weight"),
  };
  const result = await api("/api/optimize", {
    method: "POST",
    body: JSON.stringify({ weights }),
  });
  renderRanking(result);
}

function connectWeightOutputs() {
  [
    ["#learning-weight", "#learning-output"],
    ["#readiness-weight", "#readiness-output"],
    ["#risk-weight", "#risk-output"],
    ["#effort-weight", "#effort-output"],
  ].forEach(([inputSelector, outputSelector]) => {
    const input = document.querySelector(inputSelector);
    const output = document.querySelector(outputSelector);
    input.addEventListener("input", () => {
      output.value = input.value;
    });
  });
}

async function initialize() {
  try {
    const summary = await api("/api/summary");
    renderScores(summary.scores);
    renderBars("#source-chart", summary.source_states, "evidence_status");
    renderBars("#experiment-chart", summary.experiment_states, "execution_state");
    await setupTables();
    await rankExperiments();
  } catch (error) {
    document.querySelector("#query-status").textContent = `Workspace failed safely: ${error.message}`;
  }
}

document.querySelector("#run-query").addEventListener("click", runQuery);
document.querySelector("#weight-form").addEventListener("submit", rankExperiments);
connectWeightOutputs();
initialize();

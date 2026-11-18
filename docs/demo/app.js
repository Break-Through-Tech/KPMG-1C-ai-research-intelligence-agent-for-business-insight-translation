"use strict";

const STATIC_DEMO = document.documentElement.dataset.staticDemo === "true";

const icons = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  book: '<path d="M12 5v15M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2Z"/>',
  bookmark: '<path d="M6 3h12v18l-6-4-6 4Z"/>',
  chart: '<path d="M4 3v17h17M8 16v-4m5 4V7m5 9V4"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  back: '<path d="M20 12H4m6-6-6 6 6 6"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  external: '<path d="M14 3h7v7m0-7L10 14M10 4H4v16h16v-6"/>',
  user: '<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  shield:
    '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  file: '<path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8m-8 4h6"/>',
};
const icon = (name) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.file}</svg>`;
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
const areaLabel = (area) =>
  ({
    document_analysis_knowledge_access: "Knowledge & document intelligence",
    workflow_automation: "Workflow automation",
    ai_reliability_governance: "Trusted AI & governance",
    finance_risk_analytics: "Finance & risk",
    operations_supply_chain: "Operations & supply chain",
    customer_service: "Customer experience",
    technology_implementation_cost: "Technology & implementation",
  })[area] || "AI research";
const labels = {
  workspace: "Workspace",
  library: "Example papers",
  briefs: "Saved briefs",
  evaluation: "Evaluation",
  questions: "Research questions",
  brief: "Research brief",
  saved: "Saved brief",
  live: "Live research",
};
const runLabel = (name) => ({
  "answers_after_parser_integrated.json": "Current Qwen evaluation",
  "answers_qwen_branch_final.json": "Earlier Qwen evaluation",
  "answers_grounded.json": "Earlier Llama evaluation",
})[name] || name;
const state = {
  data: null,
  persona: "allison",
  run: null,
  mode: "saved",
  current: null,
  tab: "business",
  search: "",
  request: 0,
};
let saved = [];
try {
  const stored = JSON.parse(sessionStorage.getItem("kpmg-briefs") || "[]");
  if (Array.isArray(stored))
    saved = stored.filter(
      (x) =>
        x &&
        typeof x.question === "string" &&
        x.insight &&
        Array.isArray(x.sources) &&
        typeof x.markdown === "string",
    );
} catch {
  /* Storage is optional; the workspace still works. */
}
const main = document.querySelector("#main");
let toastTimer;
function toast(message) {
  const el = document.querySelector("#toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.hidden = true;
  }, 4000);
}
function updateCounts() {
  document.querySelector("#brief-count").textContent = saved.length;
  document.querySelector("#paper-count").textContent =
    state.data?.papers.length ?? "—";
}
function perspectiveSelect() {
  return `<label class="select-field">${icon("user")}<span>View as</span><select id="persona" aria-label="Review perspective">${state.data.personas.map((p) => `<option value="${esc(p.id)}" ${p.id === state.persona ? "selected" : ""}>${esc(p.role)}</option>`).join("")}</select></label>`;
}
function heading(title, subtitle = "", extra = "") {
  return `<div class="page-heading"><div><h1>${title}</h1>${subtitle ? `<p>${subtitle}</p>` : ""}</div>${extra}</div>`;
}
function status(message, warning = false) {
  return `<div class="status-bar ${warning ? "warning" : ""}">${icon(warning ? "info" : "shield")}<span>${message}</span></div>`;
}
function questionButton(id, label) {
  return `<button class="suggestion" data-action="question" data-id="${id}">${label}${icon("arrow")}</button>`;
}
function composer() {
  const live = state.mode === "live";
  const allArxiv = state.data.live_scope === "arxiv";
  return `<section class="composer" aria-label="Research query">
  <div class="composer-top"><div class="segmented" aria-label="Research mode"><button data-action="mode" data-mode="live" aria-pressed="${live}" ${state.data.live_configured ? "" : 'disabled title="Live arXiv search needs the local server"'}>${allArxiv || STATIC_DEMO ? "Ask arXiv" : "Ask sample"}</button><button data-action="mode" data-mode="saved" aria-pressed="${!live}">Examples</button></div></div>
  <form id="research-form"><label class="prompt-label" for="research-query">${live ? "Ask a research question" : "Explore example questions"}</label><div class="prompt-row"><input id="research-query" name="question" maxlength="2000" autocomplete="off" placeholder="${live ? allArxiv ? "Search arXiv research…" : "Ask about the sample papers…" : "Search the example questions…"}" value="${esc(state.search)}"><button class="button" type="submit">${live ? "Ask" : "Search"}${icon("arrow")}</button></div></form>
  ${live ? `<div class="suggestions live-controls"><label class="inline-label" for="model">Model</label><select id="model" class="filter-select">${state.data.models.map((m) => `<option>${esc(m)}</option>`).join("")}</select></div>` : `<div class="suggestions">${questionButton("q02", "Model routing")}${questionButton("q09", "Workflow intelligence")}${questionButton("q18", "AI reliability")}</div>`}
  <div class="composer-bottom">${perspectiveSelect()}</div></section>`;
}
function paperRow(paper, index, library = false) {
  return `<article class="paper-row"><div class="paper-number" aria-hidden="true">${String(index + 1).padStart(2, "0")}</div><div><span class="tag blue">${esc(areaLabel(paper.area))}</span><h3><button data-action="paper" data-id="${esc(paper.id)}">${esc(paper.title)}</button></h3><div class="paper-meta">arXiv · ${esc(paper.id)}</div></div>${library ? `<div class="paper-actions"><button class="button secondary compact" data-action="paper" data-id="${esc(paper.id)}">Questions ${icon("arrow")}</button><a class="button text compact" href="${esc(paper.url)}" target="_blank" rel="noopener noreferrer">Paper ${icon("external")}</a></div>` : `<button class="paper-open" data-action="paper" data-id="${esc(paper.id)}" aria-label="Explore ${esc(paper.title)}">${icon("arrow")}</button>`}</article>`;
}
function workspace() {
  main.innerHTML =
    heading("Research chat") +
    composer() +
    `<div id="workspace-results">${state.mode === "saved" ? `<div class="section-heading"><h2>Questions</h2><a href="#questions">All ${state.data.questions.length} ${icon("arrow")}</a></div>${questionList(state.data.questions.slice(0, 3))}` : ""}</div>`;
}
function questionList(questions) {
  return questions.length
    ? `<div class="query-list">${questions.map((q) => `<button class="query-item" data-action="question" data-id="${esc(q.id)}"><span class="question-id">${esc(q.id.toUpperCase())}</span><strong>${esc(q.query)}</strong>${icon("arrow")}</button>`).join("")}</div>`
    : `<div class="empty-state"><h2>No matches</h2><button class="button secondary" data-action="all-questions">All examples</button></div>`;
}
function searchQuestions(query) {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return state.data.questions.filter((q) => {
    const text = `${q.query} ${q.relevant_papers
      .map((id) => {
        const p = state.data.papers.find((p) => p.id === id);
        return p ? p.title + " " + areaLabel(p.area) : "";
      })
      .join(" ")}`.toLowerCase();
    return words.every((w) => text.includes(w));
  });
}
function library() {
  main.innerHTML =
    heading("Example papers") +
    `<div class="filters"><label class="searchbar">${icon("search")}<input id="library-search" aria-label="Search papers" placeholder="Search papers"></label><select id="area-filter" class="filter-select" aria-label="Filter by research theme"><option value="">All topics</option>${[...new Set(state.data.papers.map((p) => p.area).filter(Boolean))].map((a) => `<option value="${esc(a)}">${esc(areaLabel(a))}</option>`).join("")}</select></div><div class="section-heading"><span id="library-count">${state.data.papers.length} papers</span></div><div class="library-list" id="library-results">${state.data.papers.map((p, i) => paperRow(p, i, true)).join("")}</div>`;
}
function filterLibrary() {
  const query = document.querySelector("#library-search").value.toLowerCase();
  const area = document.querySelector("#area-filter").value;
  const papers = state.data.papers.filter(
    (p) =>
      (!area || p.area === area) &&
      `${p.title} ${p.id} ${areaLabel(p.area)}`.toLowerCase().includes(query),
  );
  document.querySelector("#library-count").textContent =
    `${papers.length} paper${papers.length === 1 ? "" : "s"}`;
  document.querySelector("#library-results").innerHTML = papers.length
    ? papers.map((p, i) => paperRow(p, i, true)).join("")
    : '<p class="no-results">No papers match these filters. Try another title or research theme.</p>';
}
function questionsPage(paperId) {
  const paper = state.data.papers.find((p) => p.id === paperId);
  main.innerHTML =
    `<a class="back-link" href="#library">${icon("back")}Example papers</a>` +
    heading(paper ? paper.title : "Example questions") +
    questionList(
      paper
        ? state.data.questions.filter((q) =>
            q.relevant_papers.includes(paperId),
          )
        : state.data.questions,
    );
}
function rich(text) {
  return esc(text).replace(/\[(\d+)\]/g, (match, rank) =>
    state.current?.sources.some((s) => s.rank === Number(rank))
      ? `<button class="citation" data-action="source" data-rank="${rank}" aria-label="Read source passage ${rank}">${rank}</button>`
      : match,
  );
}
function sourceBlock(source) {
  return `<article class="source-block"><h3>${esc(source.title)}</h3><div class="paper-meta">Passage ${source.rank} · ${esc(source.section || "Abstract")}</div><details><summary>Passage text</summary><blockquote>${esc(source.text)}</blockquote><div class="source-properties">${esc(source.chunk_id || "")}${source.published ? ` · ${esc(source.published)}` : ""}</div></details>${source.source_url ? `<a class="source-link" href="${esc(source.source_url)}" target="_blank" rel="noopener noreferrer">Open paper ${icon("external")}</a>` : ""}</article>`;
}
function conciseBusiness(text) {
  return text.replace(/^Proposed [^:]+ applications? for stakeholder review:\s*/i, "")
    .replace(/\s*The papers do not establish KPMG-specific outcomes or ROI\.\s*$/i, "");
}
function firstSentence(text) {
  const match = text.match(/^.*?[.!?](?=\s|$)/s);
  return match ? match[0] : text;
}
function briefBody() {
  const result = state.current;
  const insight = result.insight;
  const reviewIssues = [
    ...new Set([...result.checks, ...insight.validation_warnings]),
  ];
  if (state.tab === "sources")
    return result.sources.length
      ? result.sources.map(sourceBlock).join("")
      : '<p class="muted">No source passages were retrieved.</p>';
  if (state.tab === "technical")
    return `<section class="brief-section"><h2>Answer</h2><div class="rich-text">${rich(result.answer.split(/\n\s*Evidence\s*:/i)[0].trim())}</div>${result.answer.includes("Evidence:") ? `<details class="review-details"><summary>Evidence quotes</summary><div class="rich-text">${rich(result.answer.split(/\n\s*Evidence\s*:/i).slice(1).join("Evidence:").trim())}</div></details>` : ""}</section>${reviewIssues.length ? `<section class="brief-section"><h2>Source checks</h2><ul class="warning-list">${reviewIssues.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></section>` : ""}`;
  const finding = insight.what_study_found.split(/\n\s*Evidence\s*:/i)[0].trim();
  const application = conciseBusiness(insight.why_it_matters_to_kpmg);
  const action = insight.what_kpmg_could_consider;
  const actionLead = firstSentence(action);
  return `${insight.validation_warnings.length ? status("Needs review", true) : ""}
    <section class="brief-section"><h2>Finding</h2><div class="rich-text">${rich(finding)}</div></section>
    <section class="brief-section"><h2>Business use</h2><div class="rich-text">${rich(application)}</div></section>
    <section class="brief-section"><h2>Next step</h2><div class="rich-text">${rich(actionLead)}</div>${action.length > actionLead.length ? `<details class="review-details"><summary>More context</summary><div class="rich-text">${rich(action.slice(actionLead.length).trim())}</div></details>` : ""}</section>
    ${insight.validation_warnings.length ? `<section class="brief-section"><h2>Review notes</h2><ul class="warning-list">${insight.validation_warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></section>` : ""}`;
}
function renderBrief() {
  const r = state.current;
  const c = r.insight.confidence;
  const unique = [...new Map(r.sources.map((s) => [s.paper_id, s])).values()];
  const liveArxiv = r.scope === "arxiv";
  main.innerHTML = `<a class="back-link" href="#workspace">${icon("back")}Back</a><h1 class="brief-title">${esc(r.question)}</h1><div class="brief-toolbar"><div class="brief-meta"><span class="tag blue">${r.mode === "saved" ? "Example" : liveArxiv ? "arXiv" : "Sample"}</span><span class="tag amber">Review sources</span>${liveArxiv ? "" : `<span class="tag">${esc(state.data.personas.find((p) => p.id === r.persona)?.role || r.persona_name)}</span>`}</div><div class="brief-actions"><button class="button secondary" data-action="save">${icon("bookmark")}Save</button><button class="button" data-action="export">${icon("download")}Export</button></div></div><div class="brief-grid"><article class="brief-content"><div class="tabs" role="tablist" aria-label="Brief views">${(liveArxiv
    ? [["technical", "Answer"], ["sources", `Sources (${r.sources.length})`]]
    : [["business", "Brief"], ["technical", "Answer"], ["sources", `Sources (${r.sources.length})`]])
    .map(
      ([id, label]) =>
        `<button role="tab" id="tab-${id}" aria-selected="${state.tab === id}" aria-controls="brief-panel" tabindex="${state.tab === id ? 0 : -1}" data-action="tab" data-tab="${id}">${label}</button>`,
    )
    .join(
      "",
    )}</div><div class="brief-sections" id="brief-panel" role="tabpanel" aria-labelledby="tab-${state.tab}" tabindex="0">${briefBody()}</div></article><aside class="brief-aside"><div class="evidence-panel"><h3>${liveArxiv ? "Source checks" : "Evidence check"}</h3>${liveArxiv ? `<p class="check-passed">${r.checks.length ? `${r.checks.length} issue${r.checks.length === 1 ? "" : "s"} to review` : "No mechanical issues flagged"}</p>` : `<div class="evidence-tier">${esc(c?.tier || "Not assessed")}${c ? `<span>${Math.round(c.overall_score * 100)}/100</span>` : ""}</div><details class="score-details"><summary>Score details</summary>${
    c
      ? [
          ["Citation coverage", c.citation_coverage],
          ["Quote / numeric checks", c.quote_verification],
          ["Source diversity", c.source_diversity],
        ]
          .map(
            ([label, value]) =>
              `<div class="metric-row"><span>${label}</span><strong>${Math.round(value * 100)}%</strong></div><meter min="0" max="1" value="${value}" aria-label="${label}"></meter>`,
          )
          .join("")
      : ""
  }<p class="method-note">${esc(c?.rationale || "No score details available.")}</p></details>`}</div><div class="source-panel"><h3>Papers (${unique.length})</h3>${unique.map((s) => `<button class="source-preview" data-action="source" data-rank="${s.rank}">${icon("file")}<strong>${esc(s.title)}</strong></button>`).join("") || '<p class="muted">No sources.</p>'}</div></aside></div>`;
}
async function requestInsight(payload) {
  const token = ++state.request;
  main.innerHTML = `<a class="back-link" href="#workspace">${icon("back")}Back to workspace</a><div class="loading-state" role="status">${payload.mode === "live" ? "Retrieving sources and checking the evidence…" : "Preparing the research brief…"}</div>`;
  try {
    if (STATIC_DEMO && (payload.mode !== "saved" || !state.data.questions.some((q) => q.id === payload.id)
        || !state.data.personas.some((p) => p.id === payload.persona)))
      throw new Error("This public demo only includes the saved research questions.");
    const response = STATIC_DEMO
      ? await fetch(`data/insights/${payload.persona}/${payload.id}.json`)
      : await fetch("/api/insight", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
    const result = await response.json();
    if (token !== state.request) return;
    if (!response.ok)
      throw new Error(
        result.error || "The research request could not be completed.",
      );
    state.current = result;
    state.tab = result.scope === "arxiv" ? "technical" : "business";
    renderBrief();
  } catch (error) {
    if (token !== state.request) return;
    main.innerHTML =
      `<a class="back-link" href="#workspace">${icon("back")}Back to workspace</a>` +
      heading(
        "Research unavailable",
        "Your saved collection is still available.",
      ) +
      `<div class="error-box" role="alert">${esc(error.message)}</div><a class="button" href="#questions">Browse saved questions ${icon("arrow")}</a>`;
  }
}
function savedPage() {
  main.innerHTML =
    heading("Saved briefs") +
    (saved.length
      ? saved
          .map(
            (r, i) =>
              `<article class="saved-card"><h3>${esc(r.question)}</h3><div class="brief-actions"><a class="button secondary" href="#saved/${i}">Open ${icon("arrow")}</a><button class="button text" data-action="remove" data-index="${i}">Remove</button></div></article>`,
          )
          .join("")
      : `<div class="empty-state">${icon("bookmark")}<h2>No saved briefs</h2><a class="button" href="#workspace">Ask a question ${icon("arrow")}</a></div>`);
}
function evaluation() {
  const data = state.data;
  const answerable = data.questions.filter(
    (q) => q.relevant_papers.length,
  ).length;
  main.innerHTML =
    heading("Sample evaluation") +
    `<div class="summary-grid"><div class="summary-card"><span class="small-label">PAPERS</span><strong>${data.papers.length}</strong></div><div class="summary-card"><span class="small-label">QUESTIONS</span><strong>${data.questions.length}</strong></div><div class="summary-card"><span class="small-label">ANSWERABLE</span><strong>${answerable}</strong></div></div><div class="section-heading"><h2>Example questions</h2><label class="select-field">Run<select id="answer-run" aria-label="Saved answer run">${data.runs.map((r) => `<option value="${esc(r)}" ${r === state.run ? "selected" : ""}>${esc(runLabel(r))}</option>`).join("")}</select></label></div><div class="table-wrap"><table><thead><tr><th scope="col">ID</th><th scope="col">QUESTION</th><th scope="col">SOURCE</th></tr></thead><tbody>${data.questions.map((q) => `<tr><td>${esc(q.id.toUpperCase())}</td><td><button data-action="question" data-id="${esc(q.id)}">${esc(q.query)}</button></td><td><span class="tag ${q.relevant_papers.length ? "blue" : "amber"}">${q.relevant_papers.length ? q.relevant_papers.length + " paper" + (q.relevant_papers.length === 1 ? "" : "s") : "None"}</span></td></tr>`).join("")}</tbody></table></div><p class="evaluation-note">Five-paper test. These figures are not live arXiv performance.</p>`;
}
function route() {
  if (!state.data) return;
  state.request++;
  const [page = "workspace", id] = (
    location.hash.slice(1) || "workspace"
  ).split("/");
  document.querySelector("#crumb").textContent = labels[page] || "Workspace";
  document.querySelectorAll("[data-page]").forEach((a) => {
    const active =
      a.dataset.page === page ||
      (a.dataset.page === "workspace" &&
        ["brief", "questions", "live"].includes(page)) ||
      (a.dataset.page === "briefs" && page === "saved");
    a.classList.toggle("active", active);
    if (active) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  if (page === "library") library();
  else if (page === "questions") questionsPage(id);
  else if (page === "briefs") savedPage();
  else if (page === "evaluation") evaluation();
  else if (page === "brief")
    requestInsight({
      id,
      mode: "saved",
      persona: state.persona,
      run: state.run,
    });
  else if (page === "saved" && saved[Number(id)]) {
    state.current = saved[Number(id)];
    state.tab = state.current.scope === "arxiv" ? "technical" : "business";
    renderBrief();
  } else workspace();
  window.scrollTo(0, 0);
}
function navigate(hash) {
  if (location.hash === hash) route();
  else location.hash = hash;
}
function persistSaved() {
  try {
    sessionStorage.setItem("kpmg-briefs", JSON.stringify(saved));
    return true;
  } catch {
    toast("Browser storage is unavailable. Export the brief to keep a copy.");
    return false;
  }
}
function showSource(rank) {
  const source = state.current?.sources.find((s) => s.rank === rank);
  if (!source) return;
  document.querySelector("#source-content").innerHTML =
    `<span class="tag blue">SOURCE PASSAGE ${source.rank}</span><h2 id="source-title">${esc(source.title)}</h2><div class="paper-meta"><span>arXiv · ${esc(source.paper_id)}</span><span>${esc(source.section || "Section not recorded")}</span></div><blockquote>${esc(source.text)}</blockquote><p class="muted">Chunk: ${esc(source.chunk_id || "Not recorded")}</p>${source.source_url ? `<a class="source-link" href="${esc(source.source_url)}" target="_blank" rel="noopener noreferrer">Read the original paper ${icon("external")}</a>` : ""}`;
  document.querySelector("#source-dialog").showModal();
}
document.addEventListener("click", (event) => {
  if (event.target.closest(".skip-link")) {
    event.preventDefault();
    main.focus();
    main.scrollIntoView();
    return;
  }
  const link = event.target.closest('a[href^="#"]');
  if (link && link.getAttribute("href") === location.hash) {
    event.preventDefault();
    route();
    return;
  }
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (action === "question") navigate(`#brief/${button.dataset.id}`);
  else if (action === "paper") navigate(`#questions/${button.dataset.id}`);
  else if (action === "all-questions") navigate("#questions");
  else if (action === "mode") {
    state.search = document.querySelector("#research-query")?.value || "";
    state.mode = button.dataset.mode;
    workspace();
  } else if (action === "source") showSource(Number(button.dataset.rank));
  else if (action === "tab") {
    state.tab = button.dataset.tab;
    document.querySelectorAll("[role=tab]").forEach((t) => {
      t.setAttribute("aria-selected", t === button);
      t.tabIndex = t === button ? 0 : -1;
    });
    const panel = document.querySelector("#brief-panel");
    panel.setAttribute("aria-labelledby", `tab-${state.tab}`);
    panel.innerHTML = briefBody();
  } else if (action === "save" && state.current) {
    const r = state.current;
    if (
      saved.some(
        (s) =>
          s.question === r.question &&
          s.run === r.run &&
          s.persona === r.persona &&
          s.answer === r.answer,
      )
    ) {
      toast("This brief is already in your saved collection.");
      return;
    }
    saved.unshift(r);
    const stored = persistSaved();
    updateCounts();
    if (stored) toast("Brief saved for this browser tab.");
  } else if (action === "remove") {
    saved.splice(Number(button.dataset.index), 1);
    persistSaved();
    updateCounts();
    savedPage();
  } else if (action === "export" && state.current) {
    const blob = new Blob([state.current.markdown], {
      type: "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `kpmg-research-brief-${state.current.id || "live"}.md`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("Executive brief exported as Markdown.");
  } else if (action === "retry") boot();
});
document.addEventListener("submit", (event) => {
  if (event.target.id !== "research-form") return;
  event.preventDefault();
  const input = document.querySelector("#research-query");
  state.search = input.value.trim();
  if (state.mode === "live") {
    if (!state.search) {
      input.setCustomValidity("Enter a research question.");
      input.reportValidity();
      return;
    }
    requestInsight({
      mode: "live",
      question: state.search,
      persona: state.persona,
      model: document.querySelector("#model").value,
    });
  } else {
    const results = searchQuestions(state.search);
    document.querySelector("#workspace-results").innerHTML =
      `<div class="section-heading results-heading"><h2>${results.length} result${results.length === 1 ? "" : "s"}</h2><button class="button text" data-action="all-questions">All examples ${icon("arrow")}</button></div>${questionList(results)}`;
  }
});
document.addEventListener("input", (event) => {
  if (event.target.id === "library-search") filterLibrary();
  if (event.target.id === "research-query") event.target.setCustomValidity("");
});
document.addEventListener("change", (event) => {
  if (event.target.id === "persona") state.persona = event.target.value;
  if (event.target.id === "area-filter") filterLibrary();
  if (event.target.id === "answer-run") {
    state.run = event.target.value;
    toast("Selected run will be used when you open a question.");
  }
});
document.addEventListener("keydown", (event) => {
  if (
    !event.target.matches("[role=tab]") ||
    !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)
  )
    return;
  event.preventDefault();
  const tabs = [...document.querySelectorAll("[role=tab]")];
  const index = tabs.indexOf(event.target);
  const next =
    event.key === "Home"
      ? 0
      : event.key === "End"
        ? tabs.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) %
          tabs.length;
  tabs[next].focus();
  tabs[next].click();
});
window.addEventListener("hashchange", route);
async function boot() {
  try {
    const response = await fetch(STATIC_DEMO ? "data/bootstrap.json" : "/api/bootstrap");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load research.");
    state.data = data;
    state.run = data.default_run;
    state.mode = data.live_configured ? "live" : "saved";
    document
      .querySelectorAll("[data-icon]")
      .forEach((el) => (el.innerHTML = icon(el.dataset.icon)));
    updateCounts();
    route();
  } catch (error) {
    main.innerHTML =
      heading(
        "Workspace unavailable",
        "The research collection could not be loaded.",
      ) +
      `<div class="error-box" role="alert">${esc(error.message)}</div><button class="button retry" data-action="retry">Try again</button>`;
  }
}
boot();

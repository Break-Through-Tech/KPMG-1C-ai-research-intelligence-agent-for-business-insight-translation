"use strict";

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
  library: "Research library",
  briefs: "Saved briefs",
  evaluation: "Evidence & evaluation",
  questions: "Research questions",
  brief: "Research brief",
  saved: "Saved brief",
  live: "Live research",
};
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
  return `<label class="select-field">${icon("user")}<span>Review perspective</span><select id="persona" aria-label="Review perspective">${state.data.personas.map((p) => `<option value="${esc(p.id)}" ${p.id === state.persona ? "selected" : ""}>${esc(p.role)}</option>`).join("")}</select></label>`;
}
function heading(title, subtitle, extra = "") {
  return `<div class="page-heading"><div><div class="eyebrow">RESEARCH INTELLIGENCE</div><h1>${title}</h1><p>${subtitle}</p></div>${extra}</div>`;
}
function status(message, warning = false) {
  return `<div class="status-bar ${warning ? "warning" : ""}">${icon(warning ? "info" : "shield")}<span>${message}</span></div>`;
}
function questionButton(id, label) {
  return `<button class="suggestion" data-action="question" data-id="${id}">${label}${icon("arrow")}</button>`;
}
function composer() {
  const live = state.mode === "live";
  return `<section class="composer" aria-label="Research query">
  <div class="composer-top"><div class="segmented" aria-label="Research mode"><button data-action="mode" data-mode="saved" aria-pressed="${!live}">Explore saved research</button><button data-action="mode" data-mode="live" aria-pressed="${live}" ${state.data.live_configured ? "" : 'disabled title="Start the server with --live-root . to ask new questions"'}>Ask a question</button></div><span class="tag ${live ? "amber" : "blue"}">${icon(live ? "info" : "book")}${live ? "Local model · on demand" : "Saved benchmark collection"}</span></div>
  <form id="research-form"><label class="prompt-label" for="research-query">${live ? "What would you like to understand?" : "What are you exploring today?"}</label><div class="prompt-row"><input id="research-query" name="question" maxlength="2000" autocomplete="off" placeholder="${live ? "Ask a question about the indexed research…" : "Search model routing, AI agents, workflow automation…"}" aria-describedby="query-help" value="${esc(state.search)}"><button class="button" type="submit">${live ? "Generate insight" : "Explore research"}${icon("arrow")}</button></div></form>
  ${live ? `<div class="suggestions live-controls"><label class="inline-label" for="model">Local model</label><select id="model" class="filter-select">${state.data.models.map((m) => `<option>${esc(m)}</option>`).join("")}</select></div>` : `<div class="suggestions"><span>START WITH</span>${questionButton("q02", "Model routing")}${questionButton("q09", "Workflow intelligence")}${questionButton("q18", "AI reliability")}</div>`}
  <div class="composer-bottom">${perspectiveSelect()}<small id="query-help">${live ? "Uses your existing index and local model." : "Browse 25 fixed questions. No new answer is generated."}</small></div></section>`;
}
function paperRow(paper, index, library = false) {
  return `<article class="paper-row"><div class="paper-number" aria-hidden="true">${String(index + 1).padStart(2, "0")}</div><div><span class="tag blue">${esc(areaLabel(paper.area))}</span><h3><button data-action="paper" data-id="${esc(paper.id)}">${esc(paper.title)}</button></h3><div class="paper-meta"><span>arXiv · ${esc(paper.id)}</span><span>${paper.questions.length} benchmark questions</span><span>Preprint</span></div></div>${library ? `<div class="paper-actions"><button class="button secondary compact" data-action="paper" data-id="${esc(paper.id)}">Explore questions ${icon("arrow")}</button><a class="button text compact" href="${esc(paper.url)}" target="_blank" rel="noopener noreferrer">Original paper ${icon("external")}</a></div>` : `<button class="paper-open" data-action="paper" data-id="${esc(paper.id)}" aria-label="Explore ${esc(paper.title)}">${icon("arrow")}</button>`}</article>`;
}
function workspace() {
  main.innerHTML =
    heading(
      "Research into perspective.",
      "Explore emerging AI. Understand the evidence. Shape your next decision.",
      `<div class="heading-meta">${icon("book")}Public research collection</div>`,
    ) +
    composer() +
    `<div id="workspace-results"><div class="home-grid"><section><div class="section-heading"><div><h2>Inside the research</h2><p>A starting point for your next business question.</p></div><a href="#library">View library ${icon("arrow")}</a></div><div class="paper-list">${state.data.papers
      .slice(0, 3)
      .map((p, i) => paperRow(p, i))
      .join(
        "",
      )}</div></section><aside class="corpus-panel"><div class="corpus-art" aria-hidden="true"><span></span><span></span><span></span><span></span></div><div class="corpus-body"><div class="eyebrow">YOUR EVIDENCE BASE</div><h3>Small corpus.<br>Transparent foundations.</h3><p>Explore the public papers behind this research prototype.</p><div class="corpus-stats"><div><strong>${state.data.papers.length.toString().padStart(2, "0")}</strong><small>Research papers</small></div><div><strong>${state.data.questions.length}</strong><small>Benchmark questions</small></div></div><div class="corpus-note">${icon("shield")}<span>Source passages travel with every brief. Mechanical checks support review; they do not establish accuracy.</span></div><a class="button text" href="#evaluation">Explore the evaluation ${icon("arrow")}</a></div></aside></div></div>`;
}
function questionList(questions) {
  return questions.length
    ? `<div class="query-list">${questions.map((q) => `<button class="query-item" data-action="question" data-id="${esc(q.id)}"><span><small>${esc(q.id.toUpperCase())} · ${q.relevant_papers.length ? q.relevant_papers.length + " relevant paper" + (q.relevant_papers.length === 1 ? "" : "s") : "Out-of-corpus test"}</small><strong>${esc(q.query)}</strong></span>${icon("arrow")}</button>`).join("")}</div>`
    : `<div class="empty-state"><h2>No matching research</h2><p>Try “model”, “task”, “travel” or “G-CARL”. This collection contains fixed benchmark questions.</p><button class="button secondary" data-action="all-questions">Browse all questions</button></div>`;
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
    heading(
      "Research library",
      "A closer look at the papers behind the insight.",
    ) +
    `<div class="filters"><label class="searchbar">${icon("search")}<input id="library-search" aria-label="Search papers" placeholder="Search papers by title or topic"></label><select id="area-filter" class="filter-select" aria-label="Filter by research theme"><option value="">All research themes</option>${[...new Set(state.data.papers.map((p) => p.area).filter(Boolean))].map((a) => `<option value="${esc(a)}">${esc(areaLabel(a))}</option>`).join("")}</select></div><div class="section-heading"><span class="small-label" id="library-count">${state.data.papers.length} PAPERS IN THE COLLECTION</span><span class="tag">Public preprints · not peer-review verification</span></div><div class="library-list" id="library-results">${state.data.papers.map((p, i) => paperRow(p, i, true)).join("")}</div>`;
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
    `${papers.length} PAPER${papers.length === 1 ? "" : "S"} IN THE COLLECTION`;
  document.querySelector("#library-results").innerHTML = papers.length
    ? papers.map((p, i) => paperRow(p, i, true)).join("")
    : '<p class="no-results">No papers match these filters. Try another title or research theme.</p>';
}
function questionsPage(paperId) {
  const paper = state.data.papers.find((p) => p.id === paperId);
  main.innerHTML =
    `<a class="back-link" href="#library">${icon("back")}Research library</a>` +
    heading(
      paper ? "Explore the evidence" : "Research questions",
      paper ? esc(paper.title) : "Choose one of the saved benchmark questions.",
    ) +
    status(
      "These are saved model outputs. Review the source passages and validation status before using a finding.",
    ) +
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
  return `<article class="source-block"><span class="tag blue">Passage ${source.rank}</span><h3>${esc(source.title)}</h3><div class="paper-meta"><span>${esc(source.paper_id)}</span><span>${esc(source.section || "Section not recorded")}</span></div><details><summary>Read source passage</summary><blockquote>${esc(source.text)}</blockquote><div class="source-properties">Chunk: ${esc(source.chunk_id || "Not recorded")}<br>Authors: ${esc(source.authors?.join(", ") || "Not recorded")}<br>Publication date: ${esc(source.published || "Not recorded")}<br>Retrieval score: ${source.score === null ? "Not recorded in this saved run" : esc(source.score)}</div></details>${source.source_url ? `<a class="source-link" href="${esc(source.source_url)}" target="_blank" rel="noopener noreferrer">Open original paper ${icon("external")}</a>` : ""}</article>`;
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
    return `<section class="brief-section"><div class="section-kicker"><h2>Original model answer</h2></div><p class="section-label">Preserved from ${result.mode === "saved" ? esc(result.run) : "the local model"}</p><div class="rich-text">${rich(result.answer)}</div></section><section class="brief-section"><div class="section-kicker"><h2>Mechanical verification</h2></div>${status(reviewIssues.length ? "The answer has issues that require review." : "No mechanical issues were flagged. This is not a claim of factual accuracy.", !!reviewIssues.length)}${reviewIssues.length ? `<ul class="warning-list">${reviewIssues.map((w) => `<li>${esc(w)}</li>`).join("")}</ul>` : ""}</section>`;
  return `${insight.validation_warnings.length ? status("Business action withheld. The existing evidence checks found issues in this answer.", true) : ""}${[
    [
      "01",
      "What the study found",
      "Source-grounded answer",
      insight.what_study_found,
    ],
    [
      "02",
      "Why it matters",
      "Proposed business application · stakeholder review required",
      insight.why_it_matters_to_kpmg,
    ],
    [
      "03",
      "What to consider",
      "Proportionate action & guardrails",
      insight.what_kpmg_could_consider,
    ],
  ]
    .map(
      ([n, title, label, body]) =>
        `<section class="brief-section"><div class="section-kicker"><span>${n}</span><h2>${title}</h2></div><p class="section-label">${label}</p><div class="rich-text">${rich(body)}</div></section>`,
    )
    .join(
      "",
    )}${insight.validation_warnings.length ? `<section class="brief-section"><h3>Review notes</h3><ul class="warning-list">${insight.validation_warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></section>` : ""}`;
}
function renderBrief() {
  const r = state.current;
  const c = r.insight.confidence;
  const unique = [...new Map(r.sources.map((s) => [s.paper_id, s])).values()];
  main.innerHTML = `<a class="back-link" href="#workspace">${icon("back")}Back to workspace</a><div class="eyebrow">RESEARCH BRIEF · ${r.mode === "saved" ? "SAVED BENCHMARK" : "LIVE LOCAL MODEL"}</div><h1 class="brief-title">${esc(r.question)}</h1><div class="brief-toolbar"><div class="brief-meta"><span class="tag blue">${esc(r.insight.kpmg_service_area)}</span><span class="tag amber">Human review required</span><span>${unique.length} source paper${unique.length === 1 ? "" : "s"}</span></div><div class="brief-actions"><button class="button secondary" data-action="save">${icon("bookmark")}Save brief</button><button class="button" data-action="export">${icon("download")}Export brief</button></div></div>${status(r.mode === "saved" ? "Saved benchmark answer · The answer and source order are preserved. Business framing is a proposed application, not a finding from the paper." : "Generated with the existing local research pipeline. Inspect citations and limitations before stakeholder use.")}<div class="brief-grid"><article class="brief-content"><div class="tabs" role="tablist" aria-label="Brief views">${[
    ["business", "Business perspective"],
    ["technical", "Technical answer"],
    ["sources", `Sources (${r.sources.length})`],
  ]
    .map(
      ([id, label]) =>
        `<button role="tab" id="tab-${id}" aria-selected="${state.tab === id}" aria-controls="brief-panel" tabindex="${state.tab === id ? 0 : -1}" data-action="tab" data-tab="${id}">${label}</button>`,
    )
    .join(
      "",
    )}</div><div class="brief-sections" id="brief-panel" role="tabpanel" aria-labelledby="tab-${state.tab}" tabindex="0">${briefBody()}</div></article><aside class="brief-aside"><div class="evidence-panel"><h3>Evidence assessment</h3><div class="evidence-tier">${esc(c?.tier || "Not assessed")}</div><p>Mechanical evidence signal</p>${
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
  }<p class="method-note">${esc(c?.rationale || "No confidence breakdown supplied.")}<br><br>This score is not a probability of correctness.</p></div><div class="source-panel"><h3>Source papers <span class="muted">(${unique.length})</span></h3>${unique.map((s) => `<button class="source-preview" data-action="source" data-rank="${s.rank}"><span>${icon("file")}</span><span><strong>${esc(s.title)}</strong><small>arXiv · ${esc(s.paper_id)}</small></span></button>`).join("") || '<p class="muted">No retrieved sources.</p>'}</div><div class="source-panel"><h3>Review perspective</h3><p class="muted evaluation-note">${esc(state.data.personas.find((p) => p.id === r.persona)?.role || r.persona_name)}</p><p class="method-note">Illustrative stakeholder lens. This is not an approval or review by a named person.</p></div></aside></div>`;
}
async function requestInsight(payload) {
  const token = ++state.request;
  main.innerHTML = `<a class="back-link" href="#workspace">${icon("back")}Back to workspace</a><div class="loading-state" role="status">${payload.mode === "live" ? "Retrieving sources and checking the evidence…" : "Preparing the research brief…"}</div>`;
  try {
    const response = await fetch("/api/insight", {
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
    state.tab = "business";
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
    heading(
      "Saved briefs",
      "Your working collection, kept for this browser tab.",
    ) +
    status(
      "Briefs are stored in this tab’s session only. Export any brief you want to keep after the tab is closed.",
    ) +
    (saved.length
      ? saved
          .map(
            (r, i) =>
              `<article class="saved-card"><span class="tag blue">${r.mode === "saved" ? "Saved benchmark" : "Local model"}</span><h3>${esc(r.question)}</h3><small>${esc(r.persona_name)} · ${r.sources.length} passages · ${esc(r.insight.confidence?.tier || "Not assessed")}</small><div class="brief-actions"><a class="button secondary" href="#saved/${i}">Open brief ${icon("arrow")}</a><button class="button text" data-action="remove" data-index="${i}">Remove from session</button></div></article>`,
          )
          .join("")
      : `<div class="empty-state">${icon("bookmark")}<h2>Keep the research worth revisiting.</h2><p>Open a research brief and choose “Save brief” to add it to this collection.</p><a class="button" href="#workspace">Explore research ${icon("arrow")}</a></div>`);
}
function evaluation() {
  const data = state.data;
  const answerable = data.questions.filter(
    (q) => q.relevant_papers.length,
  ).length;
  main.innerHTML =
    heading(
      "Evidence, with context.",
      "Understand what this prototype measures—and what remains to be reviewed.",
    ) +
    status(
      "The figures below describe the committed benchmark. They are not live performance, answer accuracy, or validated business value.",
    ) +
    `<div class="summary-grid"><div class="summary-card"><span class="small-label">PUBLIC CORPUS</span><strong>${data.papers.length.toString().padStart(2, "0")}</strong><p>Committed arXiv preprints used for project-specific evaluation.</p></div><div class="summary-card"><span class="small-label">BENCHMARK COVERAGE</span><strong>${answerable} <span class="muted">/ ${data.questions.length}</span></strong><p>Questions labeled answerable; ${data.questions.length - answerable} intentionally test out-of-corpus abstention.</p></div><div class="summary-card"><span class="small-label">SAVED ANSWER RUNS</span><strong>${data.runs.length.toString().padStart(2, "0")}</strong><p>Recorded model runs available for inspecting answers and their source passages.</p></div></div><div class="section-heading"><div><h2>Inspect the benchmark</h2><p>Each question opens its preserved answer and mechanical evidence checks.</p></div><label class="select-field">Answer run<select id="answer-run" aria-label="Saved answer run">${data.runs.map((r) => `<option value="${esc(r)}" ${r === state.run ? "selected" : ""}>${esc(r)}</option>`).join("")}</select></label></div><div class="table-wrap"><table><thead><tr><th scope="col">QUESTION</th><th scope="col">RESEARCH QUESTION</th><th scope="col">EXPECTED COVERAGE</th></tr></thead><tbody>${data.questions.map((q) => `<tr><td>${esc(q.id.toUpperCase())}</td><td><button data-action="question" data-id="${esc(q.id)}">${esc(q.query)}</button></td><td><span class="tag ${q.relevant_papers.length ? "blue" : "amber"}">${q.relevant_papers.length ? q.relevant_papers.length + " paper" + (q.relevant_papers.length === 1 ? "" : "s") : "Abstention"}</span></td></tr>`).join("")}</tbody></table></div><p class="evaluation-note">Citation validity, literal quote matching and numeric checks are useful review signals. They do not prove semantic correctness, completeness or applicability to a client. Broader corpus evaluation and stakeholder review remain necessary.</p>`;
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
    state.tab = "business";
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
      `<div class="section-heading results-heading"><div><h2>${state.search ? "Matching research" : "All research questions"}</h2><p>${results.length} saved questions${state.search ? " for “" + esc(state.search) + "”" : ""}</p></div><button class="button text" data-action="all-questions">View all ${icon("arrow")}</button></div>${questionList(results)}`;
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
    const response = await fetch("/api/bootstrap");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load research.");
    state.data = data;
    state.run = data.default_run;
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

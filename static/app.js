const ingestStatus = document.getElementById("ingestStatus");
const extractStatus = document.getElementById("extractStatus");

const coreUl = document.getElementById("corePolicies");
const policiesUl = document.getElementById("policies");

function show(pre, obj) {
  pre.textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
}

function safeGet(id) {
  const el = document.getElementById(id);
  if (!el) console.error(`Missing element #${id}`);
  return el;
}

// ---- Boot ----
(function boot() {
  show(extractStatus, { boot: "app.js loaded ✅", time: new Date().toISOString() });

  const btnIngest = safeGet("btnIngest");
  const btnExtract = safeGet("btnExtract");
  const btnLoad = safeGet("btnLoad");

  if (btnIngest) btnIngest.addEventListener("click", addSource);
  if (btnExtract) btnExtract.addEventListener("click", extractPolicies);
  if (btnLoad) btnLoad.addEventListener("click", loadScorecard);

  // Health check
  fetch("/api/health")
    .then(r => r.json())
    .then(data => show(extractStatus, { boot: "app.js loaded ✅", health: data }))
    .catch(e => show(extractStatus, { boot: "app.js loaded ✅", error: "Health failed", details: String(e) }));
})();

// ---- Actions ----
async function addSource() {
  show(ingestStatus, { action: "Clicked ingest ✅" });

  const urlEl = safeGet("url");
  const url = (urlEl?.value || "").trim();

  if (!url) {
    show(ingestStatus, { ok: false, error: "Please paste a URL first." });
    return;
  }

  try {
    const res = await fetch("/api/sources", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { ok: false, error: "Server returned non-JSON", status: res.status, raw: text };
    }

    show(ingestStatus, { http_status: res.status, ...data });
  } catch (e) {
    show(ingestStatus, { ok: false, error: "Fetch failed", details: String(e) });
  }
}

async function extractPolicies() {
  try {
    const res = await fetch("/api/policies/extract", { method: "POST" });
    const data = await res.json();
    show(extractStatus, data);
  } catch (e) {
    show(extractStatus, { ok: false, error: "Extract failed", details: String(e) });
  }
}

async function loadScorecard() {
  await loadCorePlatform();
  await loadAllPolicies();
}

async function loadCorePlatform() {
  coreUl.innerHTML = "";
  try {
    const res = await fetch("/api/policies/core?limit=5");
    const data = await res.json();

    const title = document.getElementById("coreTitle");
    if (title) title.textContent = `Core platform (Top 5) — ${data.candidate || "Candidate"}`;

    const core = data.core_platform || [];
    if (!core.length) {
      coreUl.appendChild(emptyLi("No core policies yet. Ingest a URL, then run extraction."));
      return;
    }
    core.forEach(p => coreUl.appendChild(renderPolicyCard(p, true)));
  } catch (e) {
    coreUl.appendChild(emptyLi(`Failed to load core platform: ${String(e)}`));
  }
}

async function loadAllPolicies() {
  policiesUl.innerHTML = "";
  try {
    const res = await fetch("/api/policies?limit=50");
    const policies = await res.json();
    if (!policies.length) {
      policiesUl.appendChild(emptyLi("No policies yet. Ingest a URL, then run extraction."));
      return;
    }
    policies.forEach(p => policiesUl.appendChild(renderPolicyCard(p, false)));
  } catch (e) {
    policiesUl.appendChild(emptyLi(`Failed to load policies: ${String(e)}`));
  }
}

function renderPolicyCard(p, isCore) {
  const li = document.createElement("li");
  li.className = "policy " + (isCore ? "core" : "");

  const scorePct = Math.round((p.feasibility_score || 0) * 100);
  const links = (p.related_links || []).slice(0, 3).map(l => {
    return `<a class="link" href="${escapeAttr(l.url)}" target="_blank" rel="noreferrer">${escapeHtml(l.label)}</a>`;
  }).join("");

  li.innerHTML = `
    <div class="meta">
      <span class="tag">${escapeHtml(p.policy_area || "other")}</span>
      ${isCore ? `<span class="coreBadge">CORE PLATFORM</span>` : ""}
    </div>
    <div class="promise">${escapeHtml(p.promise || "")}</div>
    <div class="scoreRow">
      <div class="scoreLabel">Feasibility score:</div>
      <div class="scoreValue">${scorePct}%</div>
    </div>
    <div class="why">
      <div class="whyLabel">Why this score:</div>
      <div class="whyText">${escapeHtml(p.why || p.notes || "No explanation available.")}</div>
    </div>
    <div class="links">
      <div class="linksLabel">Related articles:</div>
      <div class="linksList">${links || "<span class='muted'>No links</span>"}</div>
    </div>
  `;
  return li;
}

function emptyLi(text) {
  const li = document.createElement("li");
  li.className = "empty";
  li.textContent = text;
  return li;
}

function escapeHtml(str) {
  return String(str).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
}
function escapeAttr(str) {
  return String(str).replaceAll('"', "&quot;");
}

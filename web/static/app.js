/* Agentic-Sec Demo — animation engine + Monte Carlo chart.
 *
 * Vanilla JS, no framework, no bundler. Source detection: live API first,
 * fall back to pre-rendered static JSON. Animation engine renders trace state
 * deterministically from a single integer step index per ADR-4.
 */
(function () {
  "use strict";

  // ----- Constants -----
  const STEP_INTERVAL_MS = 700; // tune empirically; named constant per ADR-4 note
  // Relative paths so the page works under GitHub Pages project URL prefix.
  const API_TRACE = "api/trace";
  const API_MC = "api/monte-carlo";
  const STATIC_TRACE = "static/data/default_trace.json";
  const STATIC_MC = "static/data/monte_carlo.json";
  const SVG_NS = "http://www.w3.org/2000/svg";

  // ----- State -----
  let traceData = null;
  let mcData = null;
  let currentStep = 0;
  let totalFrames = 0; // includes frame 0 = "both at start"
  let isPlaying = false;
  let playInterval = null;
  let isLiveMode = false;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ----- DOM refs -----
  const els = {};
  function bindEls() {
    els.playBtn = document.getElementById("trace-play");
    els.replayBtn = document.getElementById("trace-replay");
    els.scrub = document.getElementById("trace-scrub");
    els.stepLabel = document.getElementById("trace-step-label");
    els.staticSteps = document.getElementById("trace-static-steps");
    els.agentSteps = document.getElementById("trace-agent-steps");
    els.staticOutcome = document.getElementById("static-outcome");
    els.agentOutcome = document.getElementById("agent-outcome");
    els.liveControls = document.getElementById("trace-live-controls");
    els.staticNote = document.getElementById("trace-static-note");
    els.paramSeed = document.getElementById("param-seed");
    els.paramCapability = document.getElementById("param-capability");
    els.paramMaxSteps = document.getElementById("param-max-steps");
    els.paramRerun = document.getElementById("param-rerun");
    els.mcChart = document.getElementById("mc-chart");
    els.mcRunsNote = document.getElementById("mc-runs-note");
  }

  // ----- Source detection -----
  async function detectSourceAndLoad() {
    // Try live API first.
    try {
      const r = await fetch(API_TRACE + "?seed=7&capability=4&max_steps=8");
      if (r.ok) {
        traceData = await r.json();
        isLiveMode = true;
        try {
          const mcResp = await fetch(API_MC);
          if (mcResp.ok) mcData = await mcResp.json();
        } catch (_) {
          /* MC failure is non-fatal; chart will be empty */
        }
        return;
      }
    } catch (_) {
      /* fall through to static */
    }

    // Static fallback.
    isLiveMode = false;
    try {
      const tResp = await fetch(STATIC_TRACE);
      if (tResp.ok) traceData = await tResp.json();
      const mcResp = await fetch(STATIC_MC);
      if (mcResp.ok) mcData = await mcResp.json();
    } catch (_) {
      /* nothing to do; init() handles null traceData */
    }
  }

  function showLoadError() {
    const msg =
      'Could not load simulation data. If running locally, try ' +
      '<code>python agentic_security_demo.py --build-static</code> first.';
    [els.staticSteps, els.agentSteps].forEach((c) => {
      if (c) c.innerHTML = '<p class="trace-empty">' + msg + "</p>";
    });
  }

  // ----- Trace rendering -----
  function statusClass(code, sensitive) {
    if (sensitive) return "status-warn"; // 200 with sensitive_exposure = impact reached
    if (code >= 200 && code < 300) return "status-ok";
    if (code >= 400 && code < 500) return "status-err";
    return "status-warn";
  }

  function renderStep(step, displayNum, kind, isRecent) {
    const div = document.createElement("div");
    div.className = "trace-step" + (isRecent ? " recent" : "");

    const head = document.createElement("div");
    head.className = "step-head";

    const num = document.createElement("span");
    num.className = "step-num";
    num.textContent = String(displayNum);

    const tool = document.createElement("span");
    tool.className = "tool";
    tool.textContent = step.tool;

    const status = document.createElement("span");
    status.className = "status " + statusClass(step.status, step.sensitive_exposure);
    status.textContent = step.status;

    head.append(num, tool, status);

    const reason = document.createElement("div");
    reason.className = "reason";
    reason.textContent = step.reason;

    const obs = document.createElement("div");
    obs.className = "observation";
    obs.textContent = step.observation;

    div.append(head, reason, obs);

    if (kind === "agent" && step.memory_after_step && step.memory_after_step.length > 0) {
      div.appendChild(renderMemoryNote(step.memory_after_step));
    }

    return div;
  }

  function renderMemoryNote(memoryEntries) {
    const div = document.createElement("div");
    div.className = "memory-note";

    const label = document.createElement("span");
    label.className = "memory-label";
    label.textContent = "Agent memory after this step";
    div.appendChild(label);

    const ul = document.createElement("ul");
    ul.className = "memory-entries";
    memoryEntries.forEach((entry) => {
      const li = document.createElement("li");
      li.textContent = entry;
      ul.appendChild(li);
    });
    div.appendChild(ul);
    return div;
  }

  function renderColumn(container, steps, kind) {
    container.innerHTML = "";
    if (currentStep === 0) {
      container.innerHTML =
        '<p class="trace-empty">Frame 0 &mdash; both actors at start. Press play.</p>';
      return;
    }
    const visible = steps.slice(0, currentStep);
    if (visible.length === 0) {
      container.innerHTML = '<p class="trace-empty">&mdash; halted earlier &mdash;</p>';
      return;
    }
    visible.forEach((step, i) => {
      const isRecent = i === visible.length - 1;
      container.appendChild(renderStep(step, i + 1, kind, isRecent));
    });
  }

  function updateOutcome(el, actor, totalActorSteps) {
    if (!el) return;
    if (currentStep === 0 || currentStep < totalActorSteps) {
      el.className = "actor-outcome running";
      el.textContent = currentStep === 0 ? "—" : "running…";
      return;
    }
    if (actor.succeeded) {
      el.className = "actor-outcome success";
      el.textContent = "impact reached";
    } else {
      el.className = "actor-outcome stopped";
      el.textContent = actor.kind === "static" ? "stopped on 403" : "no impact";
    }
  }

  function renderTrace() {
    if (!traceData) return;
    const staticActor = traceData.actors[0];
    const agentActor = traceData.actors[1];

    renderColumn(els.staticSteps, staticActor.steps, "static");
    renderColumn(els.agentSteps, agentActor.steps, "agent");

    updateOutcome(els.staticOutcome, staticActor, staticActor.steps.length);
    updateOutcome(els.agentOutcome, agentActor, agentActor.steps.length);

    if (els.stepLabel) {
      els.stepLabel.textContent = "step " + currentStep + " / " + (totalFrames - 1);
    }
    if (els.scrub) els.scrub.value = String(currentStep);
  }

  // ----- Controls -----
  function setStep(n) {
    currentStep = Math.max(0, Math.min(totalFrames - 1, n));
    renderTrace();
  }

  function play() {
    if (isPlaying) return;
    if (currentStep >= totalFrames - 1) setStep(0); // restart from beginning if at end
    isPlaying = true;
    if (els.playBtn) els.playBtn.textContent = "❚❚ Pause";
    playInterval = setInterval(() => {
      if (currentStep < totalFrames - 1) {
        setStep(currentStep + 1);
      } else {
        pause();
      }
    }, STEP_INTERVAL_MS);
  }

  function pause() {
    if (!isPlaying) return;
    isPlaying = false;
    if (els.playBtn) els.playBtn.textContent = "▶ Play";
    if (playInterval) {
      clearInterval(playInterval);
      playInterval = null;
    }
  }

  function togglePlay() {
    if (isPlaying) pause();
    else play();
  }

  function replay() {
    pause();
    setStep(0);
    play();
  }

  // ----- Monte Carlo chart -----
  function svgEl(name, attrs) {
    const el = document.createElementNS(SVG_NS, name);
    if (attrs) {
      for (const k in attrs) el.setAttribute(k, String(attrs[k]));
    }
    return el;
  }

  function pathFor(points, xs, ys) {
    return points
      .map((pt, i) => {
        const cmd = i === 0 ? "M" : "L";
        return cmd + xs(pt[0]).toFixed(1) + "," + ys(pt[1]).toFixed(1);
      })
      .join(" ");
  }

  function renderMonteCarloChart() {
    if (!mcData || !els.mcChart) return;
    const svg = els.mcChart;
    const W = 600;
    const H = 320;
    const M = { top: 30, right: 30, bottom: 42, left: 56 };
    const innerW = W - M.left - M.right;
    const innerH = H - M.top - M.bottom;
    const xScale = (x) => M.left + ((x - 1) / 4) * innerW;
    const yScale = (y) => M.top + (1 - y) * innerH;

    while (svg.firstChild) svg.removeChild(svg.firstChild);

    // Gridlines + Y labels
    [0, 0.25, 0.5, 0.75, 1.0].forEach((yv) => {
      svg.appendChild(
        svgEl("line", {
          x1: M.left,
          y1: yScale(yv),
          x2: W - M.right,
          y2: yScale(yv),
          stroke: "#eef2f6",
          "stroke-width": "1",
        })
      );
      const label = svgEl("text", {
        x: M.left - 8,
        y: yScale(yv) + 4,
        "text-anchor": "end",
        fill: "#7a8896",
        "font-size": "11",
        "font-family": "-apple-system, sans-serif",
      });
      label.textContent = Math.round(yv * 100) + "%";
      svg.appendChild(label);
    });

    // X axis line
    svg.appendChild(
      svgEl("line", {
        x1: M.left,
        y1: H - M.bottom,
        x2: W - M.right,
        y2: H - M.bottom,
        stroke: "#d6e1ea",
        "stroke-width": "1",
      })
    );
    // Y axis line
    svg.appendChild(
      svgEl("line", {
        x1: M.left,
        y1: M.top,
        x2: M.left,
        y2: H - M.bottom,
        stroke: "#d6e1ea",
        "stroke-width": "1",
      })
    );

    // X labels
    [1, 2, 3, 4, 5].forEach((x) => {
      const label = svgEl("text", {
        x: xScale(x),
        y: H - M.bottom + 18,
        "text-anchor": "middle",
        fill: "#7a8896",
        "font-size": "11",
        "font-family": "-apple-system, sans-serif",
      });
      label.textContent = String(x);
      svg.appendChild(label);
    });

    // Axis titles
    const xTitle = svgEl("text", {
      x: M.left + innerW / 2,
      y: H - 6,
      "text-anchor": "middle",
      fill: "#526477",
      "font-size": "12",
      "font-family": "-apple-system, sans-serif",
      "font-weight": "700",
    });
    xTitle.textContent = "Capability";
    svg.appendChild(xTitle);

    const yTitle = svgEl("text", {
      x: -(M.top + innerH / 2),
      y: 16,
      "text-anchor": "middle",
      fill: "#526477",
      "font-size": "12",
      "font-family": "-apple-system, sans-serif",
      "font-weight": "700",
      transform: "rotate(-90)",
    });
    yTitle.textContent = "Success rate";
    svg.appendChild(yTitle);

    // Lines
    const rows = mcData.rows;
    const staticD = pathFor(
      rows.map((r) => [r.capability, r.static_success_rate]),
      xScale,
      yScale
    );
    const agentD = pathFor(
      rows.map((r) => [r.capability, r.agent_success_rate]),
      xScale,
      yScale
    );

    svg.appendChild(
      svgEl("path", {
        d: staticD,
        fill: "none",
        stroke: "#bd2e2e",
        "stroke-width": "3",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
      })
    );
    svg.appendChild(
      svgEl("path", {
        d: agentD,
        fill: "none",
        stroke: "#149c91",
        "stroke-width": "3",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
      })
    );

    // Markers
    rows.forEach((r) => {
      svg.appendChild(
        svgEl("circle", {
          cx: xScale(r.capability),
          cy: yScale(r.static_success_rate),
          r: "4",
          fill: "#bd2e2e",
        })
      );
      svg.appendChild(
        svgEl("circle", {
          cx: xScale(r.capability),
          cy: yScale(r.agent_success_rate),
          r: "4",
          fill: "#149c91",
        })
      );
    });

    // Legend
    const legendY = M.top + 8;
    const legendX = W - M.right - 150;
    [
      { label: "Static automation", color: "#bd2e2e", dx: 0 },
      { label: "Agentic executor", color: "#149c91", dx: 0 },
    ].forEach((it, i) => {
      const yy = legendY + i * 18;
      svg.appendChild(svgEl("circle", { cx: legendX, cy: yy, r: "5", fill: it.color }));
      const t = svgEl("text", {
        x: legendX + 10,
        y: yy + 4,
        fill: "#10243d",
        "font-size": "12",
        "font-family": "-apple-system, sans-serif",
        "font-weight": "700",
      });
      t.textContent = it.label;
      svg.appendChild(t);
    });

    if (els.mcRunsNote) {
      els.mcRunsNote.textContent =
        "Runs per capability: " +
        mcData.params.runs +
        ". Same step budget for both actors.";
    }
  }

  // ----- Live-only rerun -----
  async function rerun() {
    const seed = parseInt(els.paramSeed.value || "7", 10) || 7;
    const capability = Math.max(
      1,
      Math.min(5, parseInt(els.paramCapability.value || "4", 10) || 4)
    );
    const maxSteps = Math.max(
      2,
      Math.min(20, parseInt(els.paramMaxSteps.value || "8", 10) || 8)
    );

    pause();
    try {
      const r = await fetch(
        API_TRACE + "?seed=" + seed + "&capability=" + capability + "&max_steps=" + maxSteps
      );
      if (r.ok) traceData = await r.json();
      const mcResp = await fetch(API_MC + "?max_steps=" + maxSteps);
      if (mcResp.ok) mcData = await mcResp.json();
      initFromData();
    } catch (e) {
      console.error("Re-run failed:", e);
    }
  }

  // ----- Init -----
  function initFromData() {
    if (!traceData) return;
    const a = traceData.actors[0].steps.length;
    const b = traceData.actors[1].steps.length;
    totalFrames = Math.max(a, b) + 1; // frame 0 = both at start
    currentStep = reducedMotion ? totalFrames - 1 : 0;
    if (els.scrub) els.scrub.max = String(totalFrames - 1);
    renderTrace();
    renderMonteCarloChart();
  }

  async function init() {
    bindEls();
    await detectSourceAndLoad();

    if (!traceData) {
      showLoadError();
      return;
    }

    if (isLiveMode) {
      if (els.liveControls) els.liveControls.hidden = false;
      if (els.staticNote) els.staticNote.hidden = true;
      if (els.paramRerun) els.paramRerun.addEventListener("click", rerun);
    } else {
      if (els.liveControls) els.liveControls.hidden = true;
      if (els.staticNote) els.staticNote.hidden = false;
    }

    initFromData();

    if (els.playBtn) els.playBtn.addEventListener("click", togglePlay);
    if (els.replayBtn) els.replayBtn.addEventListener("click", replay);
    if (els.scrub) {
      els.scrub.addEventListener("input", (e) => {
        pause();
        setStep(parseInt(e.target.value, 10));
      });
    }

    // Keyboard: space toggles play, arrows scrub.
    document.addEventListener("keydown", (e) => {
      const tag = e.target && e.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.code === "Space") {
        e.preventDefault();
        togglePlay();
      } else if (e.code === "ArrowLeft") {
        pause();
        setStep(currentStep - 1);
      } else if (e.code === "ArrowRight") {
        pause();
        setStep(currentStep + 1);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

/* ---------------------------------------------------------------------------
 * Controls section — toggle-driven re-render of #controls-trace.
 *
 * Lives in its own IIFE so the existing #trace animation engine above is
 * untouched. Mode detection (live vs. static) is performed independently:
 * a probe to /api/trace decides which fetch path is used. Static mode loads
 * the pre-rendered catalog via window.ControlsOverlay (controls-overlay.js).
 * --------------------------------------------------------------------------- */
(function () {
  "use strict";

  var API_TRACE = "api/trace";
  var DEBOUNCE_MS = 120;
  var CAPTION_FRICTION = "Friction added. Path changed. Goal still pursued.";
  var CAPTION_INTERRUPT = "The loop is interrupted, not just the call.";
  var REPO_URL = "https://github.com/rseveymant/agentic-sec-new";
  var SERVE_CMD = "python agentic_security_demo.py --serve";

  // Mode is set by detectMode(); 'live' or 'static'.
  var mode = null;
  var debounceTimer = null;
  // Keep track of the most recent live request so out-of-order responses
  // from rapid toggling don't clobber a newer render.
  var liveReqId = 0;
  // Static mode: gate toggles until the catalog has loaded.
  var togglesDisabled = false;

  // ---- DOM refs ----
  var els = {};

  function bindEls() {
    els.fieldsets = document.querySelectorAll("#controls fieldset");
    els.checkboxes = document.querySelectorAll(
      '#controls fieldset input[type="checkbox"]'
    );
    els.resetBtn = document.getElementById("controls-reset");
    els.controlsTrace = document.getElementById("controls-trace");
    els.detectionSignal = document.getElementById("detection-signal");
    els.caption = document.getElementById("controls-caption");
    // Reuse seed/capability/max_steps inputs from the #trace section if present.
    els.paramSeed = document.getElementById("param-seed");
    els.paramCapability = document.getElementById("param-capability");
    els.paramMaxSteps = document.getElementById("param-max-steps");
  }

  // ---- Toggle state ----
  function readToggleState() {
    var tc = [];
    var ac = [];
    var checked = document.querySelectorAll(
      '#controls fieldset input[type="checkbox"]:checked'
    );
    for (var i = 0; i < checked.length; i++) {
      var id = checked[i].id || "";
      if (id.indexOf("tc-") === 0) {
        tc.push(id.slice(3));
      } else if (id.indexOf("ac-") === 0) {
        ac.push(id.slice(3));
      }
    }
    tc.sort();
    ac.sort();
    return { tc: tc, ac: ac };
  }

  // ---- Mode detection ----
  // Probe via GET to /api/trace; HEAD on Python's BaseHTTPRequestHandler returns
  // 501 by default, so we use a tiny GET probe. Cheap (cached for the page).
  function detectMode() {
    return fetch(API_TRACE + "?seed=7&capability=4&max_steps=8")
      .then(function (r) {
        if (r.ok) return "live";
        return "static";
      })
      .catch(function () {
        return "static";
      });
  }

  // ---- Helpers ----
  function getParamValue(el, fallback, lo, hi) {
    if (!el) return fallback;
    var v = parseInt(el.value, 10);
    if (isNaN(v)) return fallback;
    return Math.max(lo, Math.min(hi, v));
  }

  function statusClass(code, sensitive) {
    if (sensitive) return "status-warn";
    if (code >= 200 && code < 300) return "status-ok";
    if (code >= 400 && code < 500) return "status-err";
    return "status-warn";
  }

  function isHaltStep(step) {
    return (
      typeof step.tool === "string" &&
      step.tool.length > 0 &&
      step.tool.charAt(0) === "<"
    );
  }

  // ---- Rendering ----
  function clearChildren(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
  }

  function renderAppliedControls(applied) {
    if (!applied || applied.length === 0) return null;
    var div = document.createElement("div");
    div.className = "step-applied-controls";
    var label = document.createElement("span");
    label.className = "applied-label";
    label.textContent = "controls fired:";
    var list = document.createElement("span");
    list.className = "applied-list";
    list.textContent = " " + applied.join(", ");
    div.appendChild(label);
    div.appendChild(list);
    return div;
  }

  function renderMemoryNote(memoryEntries) {
    var div = document.createElement("div");
    div.className = "memory-note";
    var label = document.createElement("span");
    label.className = "memory-label";
    label.textContent = "Agent memory after this step";
    div.appendChild(label);
    var ul = document.createElement("ul");
    ul.className = "memory-entries";
    var lastEntry = memoryEntries[memoryEntries.length - 1];
    var li = document.createElement("li");
    li.textContent = lastEntry;
    ul.appendChild(li);
    div.appendChild(ul);
    return div;
  }

  function renderHaltStep(step, displayNum) {
    var div = document.createElement("div");
    div.className = "trace-step trace-step-halt";

    var head = document.createElement("div");
    head.className = "step-head";

    var num = document.createElement("span");
    num.className = "step-num";
    num.textContent = String(displayNum);

    var tool = document.createElement("span");
    tool.className = "tool";
    tool.textContent = step.tool;

    var status = document.createElement("span");
    status.className = "status status-err";
    status.textContent = "halt";

    head.append(num, tool, status);

    var banner = document.createElement("div");
    banner.className = "halt-banner";
    banner.textContent = step.observation || "Loop halted.";

    div.append(head, banner);

    var applied = renderAppliedControls(step.applied_controls);
    if (applied) div.appendChild(applied);
    return div;
  }

  function renderStep(step, displayNum, kind) {
    if (isHaltStep(step)) return renderHaltStep(step, displayNum);

    var div = document.createElement("div");
    div.className = "trace-step";

    var head = document.createElement("div");
    head.className = "step-head";

    var num = document.createElement("span");
    num.className = "step-num";
    num.textContent = String(displayNum);

    var tool = document.createElement("span");
    tool.className = "tool";
    tool.textContent = step.tool;

    var status = document.createElement("span");
    status.className =
      "status " + statusClass(step.status, step.sensitive_exposure);
    status.textContent = step.status;

    head.append(num, tool, status);

    var reason = document.createElement("div");
    reason.className = "reason";
    reason.textContent = step.reason || "";

    var obs = document.createElement("div");
    obs.className = "observation";
    obs.textContent = step.observation || "";

    div.append(head, reason, obs);

    var applied = renderAppliedControls(step.applied_controls);
    if (applied) div.appendChild(applied);

    if (
      kind === "agent" &&
      step.memory_after_step &&
      step.memory_after_step.length > 0
    ) {
      div.appendChild(renderMemoryNote(step.memory_after_step));
    }

    return div;
  }

  function renderColumnInto(stepsContainer, steps, kind) {
    clearChildren(stepsContainer);
    if (!steps || steps.length === 0) {
      var p = document.createElement("p");
      p.className = "trace-empty";
      p.textContent =
        kind === "agent"
          ? "no steps — agent did not act."
          : "no steps.";
      stepsContainer.appendChild(p);
      return;
    }
    for (var i = 0; i < steps.length; i++) {
      stepsContainer.appendChild(renderStep(steps[i], i + 1, kind));
    }
  }

  function setOutcomePill(headerEl, actor) {
    if (!headerEl) return;
    var pill = headerEl.querySelector(".actor-outcome");
    if (!pill) return;
    if (!actor) {
      pill.className = "actor-outcome";
      pill.textContent = "—";
      return;
    }
    if (actor.succeeded) {
      pill.className = "actor-outcome success";
      pill.textContent = "impact reached";
    } else {
      pill.className = "actor-outcome stopped";
      pill.textContent = actor.kind === "static" ? "stopped on 403" : "no impact";
    }
  }

  function buildColumn(kind, actor) {
    var col = document.createElement("div");
    col.className = "trace-col " + (kind === "static" ? "trace-col-static" : "trace-col-agent");

    var header = document.createElement("div");
    header.className = "trace-col-header";

    var label = document.createElement("span");
    label.className =
      "actor-label " + (kind === "static" ? "actor-label-static" : "actor-label-agent");
    label.textContent =
      kind === "static" ? "Static automation" : "Agentic executor";

    var pill = document.createElement("span");
    pill.className = "actor-outcome";
    pill.textContent = "—";

    header.appendChild(label);
    header.appendChild(pill);
    col.appendChild(header);

    var stepsDiv = document.createElement("div");
    stepsDiv.className =
      "trace-steps " + (kind === "static" ? "trace-static" : "trace-agent");
    col.appendChild(stepsDiv);

    renderColumnInto(stepsDiv, actor ? actor.steps : [], kind);
    setOutcomePill(header, actor);
    return col;
  }

  function renderTrace(staticActor, agentActor) {
    if (!els.controlsTrace) return;
    clearChildren(els.controlsTrace);
    els.controlsTrace.classList.add("trace-columns");
    els.controlsTrace.classList.remove("controls-trace-fallback");
    els.controlsTrace.classList.remove("controls-trace-loading");
    els.controlsTrace.appendChild(buildColumn("static", staticActor));
    els.controlsTrace.appendChild(buildColumn("agent", agentActor));
  }

  function renderDetectionSignal(signal) {
    if (!els.detectionSignal) return;
    var logged = (signal && typeof signal.logged === "number") ? signal.logged : 0;
    var flagged = (signal && typeof signal.flagged === "number") ? signal.flagged : 0;
    clearChildren(els.detectionSignal);
    var pillL = document.createElement("span");
    pillL.className = "signal-pill signal-pill-logged";
    pillL.textContent = "▣ " + logged + " logged";
    var pillF = document.createElement("span");
    pillF.className = "signal-pill signal-pill-flagged";
    pillF.textContent = "⚠ " + flagged + " flagged";
    els.detectionSignal.appendChild(pillL);
    els.detectionSignal.appendChild(pillF);
  }

  function renderCaption(agentActor, anyControlsOn) {
    if (!els.caption) return;
    if (!agentActor || !anyControlsOn) {
      els.caption.textContent = "";
      els.caption.hidden = true;
      return;
    }
    var halt = agentActor.agentic_halt_reason;
    if (
      agentActor.succeeded === true &&
      (halt === null || halt === undefined)
    ) {
      els.caption.textContent = CAPTION_FRICTION;
      els.caption.hidden = false;
      return;
    }
    if (halt === "govern" || halt === "contain" || halt === "respond") {
      els.caption.textContent = CAPTION_INTERRUPT;
      els.caption.hidden = false;
      return;
    }
    // Other failure shapes (e.g., agent ran out of steps without an agentic
    // halt). Hide the caption rather than misclassifying.
    els.caption.textContent = "";
    els.caption.hidden = true;
  }

  function renderLoading() {
    if (!els.controlsTrace) return;
    clearChildren(els.controlsTrace);
    els.controlsTrace.classList.remove("trace-columns");
    els.controlsTrace.classList.add("controls-trace-loading");
    var p = document.createElement("p");
    p.className = "trace-empty";
    p.textContent = "Loading control catalog…";
    els.controlsTrace.appendChild(p);
  }

  function renderFallback(state) {
    if (!els.controlsTrace) return;
    clearChildren(els.controlsTrace);
    els.controlsTrace.classList.remove("trace-columns");
    els.controlsTrace.classList.add("controls-trace-fallback");

    var wrap = document.createElement("div");
    wrap.className = "controls-fallback";

    var heading = document.createElement("p");
    heading.className = "controls-fallback-heading";
    var headingStrong = document.createElement("strong");
    headingStrong.textContent = "This combination requires the live demo.";
    heading.appendChild(headingStrong);
    wrap.appendChild(heading);

    var body = document.createElement("p");
    body.className = "controls-fallback-body";
    body.textContent =
      "The static snapshot does not include a pre-rendered trace for this set of toggles. Run the live demo to see the agent's behavior on this combination.";
    wrap.appendChild(body);

    var togglesLine = document.createElement("p");
    togglesLine.className = "controls-fallback-toggles";
    var labelStrong = document.createElement("strong");
    labelStrong.textContent = "Toggles set: ";
    togglesLine.appendChild(labelStrong);
    var tcText = state.tc.length ? state.tc.join(", ") : "(none)";
    var acText = state.ac.length ? state.ac.join(", ") : "(none)";
    togglesLine.appendChild(
      document.createTextNode("traditional = " + tcText + "; agentic = " + acText)
    );
    wrap.appendChild(togglesLine);

    var howto = document.createElement("p");
    howto.className = "controls-fallback-howto";
    howto.appendChild(document.createTextNode("Clone "));
    var a = document.createElement("a");
    a.href = REPO_URL;
    a.textContent = REPO_URL;
    howto.appendChild(a);
    howto.appendChild(document.createTextNode(" and run "));
    var code = document.createElement("code");
    code.textContent = SERVE_CMD;
    howto.appendChild(code);
    howto.appendChild(document.createTextNode("."));
    wrap.appendChild(howto);

    els.controlsTrace.appendChild(wrap);
  }

  // ---- Trace shape adapter ----
  // Live API returns { actors: [staticActor, agentActor], detection_signal }.
  // Static catalog returns { static_actor_trace, agent_traces[*].trace }.
  // Normalize into { staticActor, agentActor, detection_signal }.
  function normalizeLive(json) {
    if (!json || !json.actors) return null;
    return {
      staticActor: json.actors[0] || null,
      agentActor: json.actors[1] || null,
      detection_signal: json.detection_signal || { logged: 0, flagged: 0 },
    };
  }

  function normalizeStatic(lookupResult) {
    if (!lookupResult || lookupResult.fallback) return null;
    return {
      staticActor: lookupResult.static_actor_trace || null,
      agentActor: lookupResult.trace || null,
      detection_signal:
        lookupResult.detection_signal || { logged: 0, flagged: 0 },
    };
  }

  // ---- Render orchestration ----
  function renderFromNormalized(normalized, anyControlsOn) {
    if (!normalized) return;
    renderTrace(normalized.staticActor, normalized.agentActor);
    renderDetectionSignal(normalized.detection_signal);
    renderCaption(normalized.agentActor, anyControlsOn);
  }

  function fetchLiveAndRender() {
    var state = readToggleState();
    var anyOn = state.tc.length + state.ac.length > 0;
    var seed = getParamValue(els.paramSeed, 7, 0, 99999);
    var capability = getParamValue(els.paramCapability, 4, 1, 5);
    var maxSteps = getParamValue(els.paramMaxSteps, 8, 2, 20);
    var url =
      API_TRACE +
      "?seed=" + seed +
      "&capability=" + capability +
      "&max_steps=" + maxSteps +
      "&tc=" + encodeURIComponent(state.tc.join(",")) +
      "&ac=" + encodeURIComponent(state.ac.join(","));

    var reqId = ++liveReqId;
    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("trace fetch failed: " + r.status);
        return r.json();
      })
      .then(function (json) {
        if (reqId !== liveReqId) return; // a newer request superseded this one
        var n = normalizeLive(json);
        renderFromNormalized(n, anyOn);
      })
      .catch(function (err) {
        // Quiet failure for repeated toggles; surface to console for debugging.
        // Don't blow away the existing UI.
        if (typeof console !== "undefined" && console.error) {
          console.error("controls live fetch error:", err);
        }
      });
  }

  function lookupStaticAndRender() {
    if (!window.ControlsOverlay) return;
    var state = readToggleState();
    var anyOn = state.tc.length + state.ac.length > 0;
    var result = window.ControlsOverlay.lookupTrace(state.tc, state.ac);
    if (result.fallback) {
      renderFallback(state);
      // Detection signal stays at zero for fallback combos.
      renderDetectionSignal({ logged: 0, flagged: 0 });
      // Caption hidden when fallback.
      if (els.caption) {
        els.caption.textContent = "";
        els.caption.hidden = true;
      }
      return;
    }
    var n = normalizeStatic(result);
    renderFromNormalized(n, anyOn);
  }

  function triggerRender() {
    if (mode === "live") {
      fetchLiveAndRender();
    } else if (mode === "static") {
      lookupStaticAndRender();
    }
  }

  function debouncedTrigger() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      debounceTimer = null;
      triggerRender();
    }, DEBOUNCE_MS);
  }

  // ---- Default-state render (no controls toggled) ----
  function renderDefaultState() {
    if (mode === "live") {
      fetchLiveAndRender();
    } else if (mode === "static") {
      // The static catalog includes the all-off entry.
      lookupStaticAndRender();
    }
  }

  // ---- Toggle gating during static-mode load ----
  function setTogglesDisabled(disabled) {
    togglesDisabled = disabled;
    for (var i = 0; i < els.checkboxes.length; i++) {
      els.checkboxes[i].disabled = disabled;
    }
    if (els.resetBtn) els.resetBtn.disabled = disabled;
  }

  // ---- Reset ----
  function resetAll() {
    if (togglesDisabled) return;
    for (var i = 0; i < els.checkboxes.length; i++) {
      els.checkboxes[i].checked = false;
    }
    // Render synchronously rather than waiting for a debounce — Reset is a
    // single deliberate user action.
    triggerRender();
  }

  // ---- Static script loader ----
  // If the page didn't include controls-overlay.js as a static <script>,
  // dynamically inject it. Index.html includes it via <script defer>, so this
  // is a defensive no-op in the canonical layout.
  function ensureOverlayLoaded() {
    if (window.ControlsOverlay) return Promise.resolve();
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = "static/controls-overlay.js";
      s.defer = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("controls-overlay.js load failed")); };
      document.head.appendChild(s);
    });
  }

  // ---- Wire-up ----
  function attachListeners() {
    for (var i = 0; i < els.checkboxes.length; i++) {
      els.checkboxes[i].addEventListener("change", debouncedTrigger);
    }
    if (els.resetBtn) {
      els.resetBtn.addEventListener("click", resetAll);
    }
  }

  function init() {
    bindEls();
    if (!els.controlsTrace) return; // Section not present (older page); no-op.

    attachListeners();

    detectMode().then(function (m) {
      mode = m;
      if (mode === "live") {
        renderDefaultState();
        return;
      }
      // Static mode: gate toggles, load catalog, then render.
      setTogglesDisabled(true);
      renderLoading();
      ensureOverlayLoaded()
        .then(function () {
          return window.ControlsOverlay.loadCatalog();
        })
        .then(function () {
          setTogglesDisabled(false);
          renderDefaultState();
        })
        .catch(function (err) {
          if (typeof console !== "undefined" && console.error) {
            console.error("controls-overlay load failed:", err);
          }
          // Leave toggles disabled; show a clear note.
          if (els.controlsTrace) {
            clearChildren(els.controlsTrace);
            els.controlsTrace.classList.remove("trace-columns");
            var p = document.createElement("p");
            p.className = "trace-empty";
            p.textContent =
              "Could not load control catalog. Refresh to retry.";
            els.controlsTrace.appendChild(p);
          }
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

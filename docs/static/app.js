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

/* Agentic-Sec Demo — static-mode catalog overlay.
 *
 * Loaded by app.js when the live API is unreachable. One-shot fetch of the
 * pre-rendered superset trace catalog; lookup by canonical control-set key.
 *
 * The JS does NOT re-implement the simulator (per ADR-7-3). It only indexes
 * `agent_traces[*].covers` entries and matches the current toggle state's
 * canonical key against that index.
 */
(function () {
  "use strict";

  // Relative path so the page works under GitHub Pages project URL prefix.
  // Mirrors the /static/ asset prefix used elsewhere in the page.
  var CATALOG_URL = "static/data/superset_trace.json";

  var catalog = null;
  var loadPromise = null;
  var index = null; // Map<string, CatalogEntry>
  var staticActorTrace = null;

  function canonicalKey(tcArr, acArr) {
    var tc = (tcArr || []).slice().sort().join(",");
    var ac = (acArr || []).slice().sort().join(",");
    return "tc=" + tc + ";ac=" + ac;
  }

  function buildIndex(parsed) {
    var idx = Object.create(null);
    var entries = (parsed && parsed.agent_traces) || [];
    for (var i = 0; i < entries.length; i++) {
      var entry = entries[i];
      var covers = entry.covers || [];
      for (var j = 0; j < covers.length; j++) {
        var c = covers[j];
        // covers entries are stored with already-sorted tc/ac arrays
        // (per Unit B's catalog builder), but we re-sort defensively
        // to keep this independent of producer assumptions.
        var key = canonicalKey(c.tc || [], c.ac || []);
        idx[key] = entry;
      }
    }
    return idx;
  }

  function loadCatalog() {
    if (loadPromise) return loadPromise;
    loadPromise = fetch(CATALOG_URL)
      .then(function (r) {
        if (!r.ok) throw new Error("catalog fetch failed: " + r.status);
        return r.json();
      })
      .then(function (parsed) {
        catalog = parsed;
        staticActorTrace = parsed.static_actor_trace || null;
        index = buildIndex(parsed);
      })
      .catch(function (err) {
        // Reset so a future caller could retry; surface error.
        loadPromise = null;
        throw err;
      });
    return loadPromise;
  }

  function catalogReady() {
    return catalog !== null && index !== null;
  }

  function lookupTrace(tcArr, acArr) {
    if (!catalogReady()) return { fallback: true };
    var key = canonicalKey(tcArr, acArr);
    var entry = index[key];
    if (!entry) return { fallback: true };
    return {
      trace: entry.trace,
      detection_signal: entry.detection_signal,
      static_actor_trace: staticActorTrace,
      fallback: false,
    };
  }

  function getStaticActorTrace() {
    return staticActorTrace;
  }

  // Public surface — attached to a single global namespace to avoid polluting
  // the window with multiple module-shaped names.
  window.ControlsOverlay = {
    loadCatalog: loadCatalog,
    catalogReady: catalogReady,
    lookupTrace: lookupTrace,
    canonicalKey: canonicalKey,
    getStaticActorTrace: getStaticActorTrace,
  };
})();

(() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
    get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
  }) : x)(function(x) {
    if (typeof require !== "undefined") return require.apply(this, arguments);
    throw Error('Dynamic require of "' + x + '" is not supported');
  });
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    // If the importer is in node compatibility mode or this is not an ESM
    // file that has been converted to a CommonJS file using a Babel-
    // compatible transform (i.e. "__esModule" has not been set), then set
    // "default" to the CommonJS "module.exports" for node compatibility.
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));

  // ../components/confrontation-log-client.tsx
  var import_react2 = __toESM(__require("react"), 1);
  var import_client = __require("react-dom/client");

  // ../components/ConfrontationLog.tsx
  var import_react = __toESM(__require("react"), 1);

  // ../components/lib/apiClient.ts
  async function getConfrontationLogs(campaignId) {
    const res = await fetch(`/api/campaign/${encodeURIComponent(campaignId)}/confrontations`);
    if (!res.ok) {
      throw new Error(`Failed to fetch confrontation logs: ${res.status}`);
    }
    const data = await res.json();
    return data.confrontations;
  }

  // ../components/ConfrontationLog.tsx
  var ConfrontationLog = ({ campaignId, identityScopeId }) => {
    const id = campaignId || identityScopeId;
    const [logs, setLogs] = (0, import_react.useState)([]);
    const [loading, setLoading] = (0, import_react.useState)(true);
    const [error, setError] = (0, import_react.useState)(null);
    const [isCollapsed, setIsCollapsed] = (0, import_react.useState)(false);
    const [isHydrated, setIsHydrated] = (0, import_react.useState)(false);
    const containerRef = (0, import_react.useRef)(null);
    const isValidIdentity = id && id.trim() !== "";
    (0, import_react.useEffect)(() => {
      const savedState = localStorage.getItem("clog_collapsed");
      if (savedState !== null) {
        setIsCollapsed(savedState === "true");
      }
    }, []);
    const toggleCollapse = (0, import_react.useCallback)(() => {
      const newState = !isCollapsed;
      setIsCollapsed(newState);
      localStorage.setItem("clog_collapsed", newState.toString());
    }, [isCollapsed]);
    const triggerHydration = (0, import_react.useCallback)(() => {
      if (!isHydrated && isValidIdentity) {
        setIsHydrated(true);
      }
    }, [isHydrated, isValidIdentity]);
    (0, import_react.useEffect)(() => {
      if (!isHydrated && isValidIdentity && containerRef.current) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                triggerHydration();
                observer.disconnect();
              }
            });
          },
          { threshold: 0.1 }
        );
        observer.observe(containerRef.current);
        return () => observer.disconnect();
      }
    }, [isHydrated, isValidIdentity, triggerHydration]);
    (0, import_react.useEffect)(() => {
      if (!isHydrated || !isValidIdentity) return;
      setLoading(true);
      setError(null);
      getConfrontationLogs(id).then(setLogs).catch((e) => {
        setError(e.message);
        console.warn("Confrontation Log fetch error:", e.message);
      }).finally(() => setLoading(false));
    }, [isHydrated, id, isValidIdentity]);
    if (!isValidIdentity) {
      console.warn("Confrontation Log: Missing or invalid identity_scope_id");
      return /* @__PURE__ */ import_react.default.createElement(
        "div",
        {
          "data-testid": "confrontation-log",
          className: "bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4"
        },
        /* @__PURE__ */ import_react.default.createElement("div", { className: "text-sm text-gray-500 italic" }, "Confrontation Log unavailable - missing campaign identifier")
      );
    }
    if (!isHydrated) {
      return /* @__PURE__ */ import_react.default.createElement(
        "div",
        {
          ref: containerRef,
          "data-testid": "confrontation-log",
          className: "bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4"
        },
        /* @__PURE__ */ import_react.default.createElement("div", { className: "flex items-center justify-between" }, /* @__PURE__ */ import_react.default.createElement("h3", { className: "text-lg font-semibold text-gray-700" }, "Confrontation Log"), /* @__PURE__ */ import_react.default.createElement(
          "button",
          {
            "data-testid": "clog-toggle",
            onClick: triggerHydration,
            className: "px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          },
          "Show Log"
        )),
        /* @__PURE__ */ import_react.default.createElement("div", { className: "text-sm text-gray-500 mt-2" }, "Click to load confrontation history")
      );
    }
    return /* @__PURE__ */ import_react.default.createElement(
      "div",
      {
        ref: containerRef,
        "data-testid": "confrontation-log",
        className: "bg-white border border-gray-200 rounded-lg shadow-sm mb-4 overflow-hidden"
      },
      /* @__PURE__ */ import_react.default.createElement("div", { className: "flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200" }, /* @__PURE__ */ import_react.default.createElement("h3", { className: "text-lg font-semibold text-gray-800" }, "Confrontation Log"), /* @__PURE__ */ import_react.default.createElement(
        "button",
        {
          "data-testid": "clog-toggle",
          onClick: toggleCollapse,
          className: "flex items-center gap-2 px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
        },
        isCollapsed ? "Show" : "Hide",
        /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs" }, isCollapsed ? "\u25BC" : "\u25B2")
      )),
      !isCollapsed && /* @__PURE__ */ import_react.default.createElement("div", { className: "p-4" }, loading && /* @__PURE__ */ import_react.default.createElement("div", { className: "flex items-center justify-center py-8" }, /* @__PURE__ */ import_react.default.createElement("div", { className: "animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" }), /* @__PURE__ */ import_react.default.createElement("span", { className: "ml-2 text-gray-500" }, "Loading confrontation log...")), error && /* @__PURE__ */ import_react.default.createElement(
        "div",
        {
          "data-testid": "clog-error",
          className: "p-4 text-red-600 bg-red-50 border border-red-200 rounded-lg"
        },
        /* @__PURE__ */ import_react.default.createElement("div", { className: "font-medium" }, "Error loading confrontation log"),
        /* @__PURE__ */ import_react.default.createElement("div", { className: "text-sm mt-1" }, error)
      ), !loading && !error && logs.length === 0 && /* @__PURE__ */ import_react.default.createElement(
        "div",
        {
          "data-testid": "clog-empty",
          className: "p-4 text-gray-500 bg-gray-50 rounded-lg text-center"
        },
        /* @__PURE__ */ import_react.default.createElement("div", { className: "text-sm italic" }, "No confrontations have been logged for this campaign.")
      ), !loading && !error && logs.length > 0 && /* @__PURE__ */ import_react.default.createElement("div", { className: "space-y-3" }, logs.map((entry) => {
        var _a;
        return /* @__PURE__ */ import_react.default.createElement(
          "div",
          {
            key: entry.arc_id + entry.timestamp,
            "data-testid": "clog-entry",
            className: "rounded-lg border border-gray-200 bg-gray-50/50 p-4 flex flex-col gap-3 hover:bg-gray-50 transition-colors"
          },
          /* @__PURE__ */ import_react.default.createElement("div", { className: "flex flex-wrap items-center gap-2 justify-between" }, /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs text-gray-500 font-medium" }, "\u{1F553} ", new Date(entry.timestamp).toLocaleString(void 0, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
          })), /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 font-semibold" }, "\u{1F3AF} ", entry.confrontation_type), /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800 font-semibold" }, "\u{1F9E0} ", entry.identity_label), /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800 font-mono" }, "\u{1F4CD} ", entry.arc_id), /* @__PURE__ */ import_react.default.createElement("span", { className: "flex items-center gap-1" }, /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs" }, "\u{1F4A5}"), /* @__PURE__ */ import_react.default.createElement("span", { className: "w-20 h-2 bg-gray-200 rounded-full overflow-hidden" }, /* @__PURE__ */ import_react.default.createElement(
            "span",
            {
              className: "block h-full rounded-full bg-red-500 transition-all duration-300",
              style: { width: `${Math.round(entry.severity * 100)}%` }
            }
          )), /* @__PURE__ */ import_react.default.createElement("span", { className: "text-xs font-mono text-red-700 ml-1" }, Math.round(entry.severity * 100), "%"))),
          /* @__PURE__ */ import_react.default.createElement("div", { className: "text-sm text-gray-700 leading-relaxed" }, entry.message || ((_a = entry.contradiction_summary) == null ? void 0 : _a.description) || /* @__PURE__ */ import_react.default.createElement("span", { className: "italic text-gray-400" }, "No details available"))
        );
      })))
    );
  };
  var ConfrontationLog_default = ConfrontationLog;

  // ../components/confrontation-log-client.tsx
  var rootElement = document.getElementById("confrontation-log-root");
  if (rootElement) {
    const identityScopeId = rootElement.getAttribute("data-identity-scope-id") || "";
    const root = (0, import_client.createRoot)(rootElement);
    root.render(/* @__PURE__ */ import_react2.default.createElement(ConfrontationLog_default, { identityScopeId }));
  }
})();
//# sourceMappingURL=confrontation-log-client.js.map

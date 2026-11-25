/* Kindling site navigation: one bar across every space (Home, Engine, Development, Discovery).
 *
 * BEFORE PUBLISHING: set ENABLED to false, or delete this file. Pages work without it:
 * the bar disappears, the space offsets drop to zero, and cross-space links (elements with
 * data-space) stay as plain text, so nothing points at a page that is not published.
 */
(function () {
  var ENABLED = true;
  if (!ENABLED) return;

  var me = document.currentScript;
  var root = me.src.replace(/shared\/sitenav\.js(\?.*)?$/, "");
  var SPACES = [
    { id: "home", path: "index.html", label: "Kindling" },
    { id: "engine", path: "engine.html", label: "Engine" },
    { id: "dev", path: "dev-dashboard.html", label: "Development" },
    { id: "discovery", path: "discovery/index.html", label: "Discovery" }
  ];
  var here = location.href.split("#")[0].split("?")[0];
  function isCurrent(s) {
    var url = root + s.path;
    if (s.id === "discovery") return here.indexOf(root + "discovery/") === 0;
    return here === url || (s.id === "home" && here === root);
  }

  var css = [
    ":root{--sitenav-h:48px}",
    ".ksn{position:fixed;top:0;left:0;right:0;height:48px;z-index:50;background:#171C20;color:#C9D0CC;",
    "font:500 15px/1 'Archivo',system-ui,sans-serif;display:flex;align-items:stretch;border-bottom:1px solid #2E363C}",
    ".ksn a{color:inherit;text-decoration:none;display:flex;align-items:center;padding:0 16px;white-space:nowrap;position:relative}",
    ".ksn a:hover{color:#fff;background:#232A30}",
    ".ksn a:focus-visible{outline:2px solid #E8743B;outline-offset:-2px;color:#fff}",
    ".ksn .home{font-weight:800;font-size:17px;color:#fff;padding-right:22px;font-variation-settings:'wdth' 120}",
    ".ksn .sp{display:flex;overflow-x:auto;scrollbar-width:none}",
    ".ksn .sp::-webkit-scrollbar{display:none}",
    ".ksn a[aria-current]{color:#fff}",
    ".ksn a[aria-current]::after{content:'';position:absolute;left:16px;right:16px;bottom:0;height:3px;background:#E8743B}",
    ".ksn .skip{position:absolute;left:-9999px}",
    ".ksn .skip:focus{left:8px;top:6px;height:36px;background:#E8743B;color:#fff;z-index:2}",
    "body{padding-top:48px}",
    "[data-space][href]{text-decoration:underline}",
    "@media print{.ksn{display:none}body{padding-top:0}}"
  ].join("");
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var nav = document.createElement("nav");
  nav.className = "ksn";
  nav.setAttribute("aria-label", "Kindling spaces");
  var main = document.getElementById("main-content") || document.querySelector("main") || document.body;
  if (!main.id) main.id = "main-content";
  var html = '<a class="skip" href="#' + main.id + '">Skip to content</a>';
  var home = SPACES[0];
  html += '<a class="home" href="' + root + home.path + '"' + (isCurrent(home) ? ' aria-current="page"' : "") + ">" + home.label + "</a>";
  html += '<div class="sp">';
  SPACES.slice(1).forEach(function (s) {
    html += '<a href="' + root + s.path + '"' + (isCurrent(s) ? ' aria-current="page"' : "") + ">" + s.label + "</a>";
  });
  html += "</div>";
  nav.innerHTML = html;
  document.body.insertBefore(nav, document.body.firstChild);
  document.documentElement.classList.add("has-sitenav");

  // Cross-space links in page content become links only while the site nav is on.
  var byId = {};
  SPACES.forEach(function (s) { byId[s.id] = root + s.path; });
  document.querySelectorAll("[data-space]").forEach(function (el) {
    var t = byId[el.getAttribute("data-space")];
    if (t) el.setAttribute("href", t + (el.getAttribute("data-hash") || ""));
  });
})();

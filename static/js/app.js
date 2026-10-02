// Acik/koyu tema tercihi (yalnizca bu tarayicida saklanir)
(function () {
  try {
    var saved = localStorage.getItem("bp_theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) {}
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    var root = document.documentElement;
    var cur = root.getAttribute("data-theme") ||
      (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
    var next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("bp_theme", next); } catch (e) {}
  });
  // acik olan tek bir dropdown kalsin
  document.addEventListener("toggle", function (e) {
    if (e.target.tagName !== "DETAILS" || !e.target.open) return;
    document.querySelectorAll("details[open]").forEach(function (d) {
      if (d !== e.target) d.open = false;
    });
  }, true);
})();

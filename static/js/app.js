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

// Kategori seritleri: scrollbar yok; fare tekerigi ve surukleme ile yatay kayar
(function () {
  function bind(el) {
    var down = false, sx = 0, sl = 0, moved = false;
    el.addEventListener("wheel", function (e) {
      if (el.scrollWidth <= el.clientWidth) return;
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) { el.scrollLeft += e.deltaY; e.preventDefault(); }
    }, { passive: false });
    el.addEventListener("mousedown", function (e) { down = true; moved = false; sx = e.pageX; sl = el.scrollLeft; });
    window.addEventListener("mouseup", function () { down = false; el.classList.remove("drag"); });
    window.addEventListener("mousemove", function (e) {
      if (!down) return;
      var dx = e.pageX - sx;
      if (Math.abs(dx) > 4) { moved = true; el.classList.add("drag"); }
      el.scrollLeft = sl - dx;
    });
    el.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  }
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".catrow, .hcat-card").forEach(bind);
  });
})();

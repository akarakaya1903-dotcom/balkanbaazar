/* Aranabilir secim kutusu: select[data-combo] alanlarini yazdikca filtreleyen kutuya cevirir.
   data-combo-add="city_new"  -> listede olmayan degeri "➕ ekle" olarak gonderir (gizli alan city_new).
   data-depends="id_country"  -> secenekleri o alanin degerine gore daraltir (option[data-country]).  */
(function () {
  function norm(s) {
    return (s || "").replace(/ı/g, "i").replace(/İ/g, "i").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function enhance(sel) {
    if (sel.dataset.comboDone) { return; }
    sel.dataset.comboDone = "1";
    var addName = sel.getAttribute("data-combo-add");
    var depId = sel.getAttribute("data-depends");
    var dep = depId ? document.getElementById(depId) : null;
    var wrap = document.createElement("div"); wrap.className = "combo";
    var inp = document.createElement("input"); inp.type = "text"; inp.className = "combo-in";
    inp.autocomplete = "off"; inp.placeholder = "🔍"; inp.setAttribute("role", "combobox");
    var list = document.createElement("ul"); list.className = "combo-list"; list.hidden = true;
    var hid = null;
    if (addName) { hid = document.createElement("input"); hid.type = "hidden"; hid.name = addName; }
    sel.parentNode.insertBefore(wrap, sel);
    wrap.appendChild(inp); wrap.appendChild(list); if (hid) { wrap.appendChild(hid); } wrap.appendChild(sel);
    sel.style.display = "none";
    var required = sel.required; sel.required = false;
    var active = -1;

    function options() {
      return [].slice.call(sel.options).filter(function (o) {
        if (!o.value) { return false; }
        if (dep && dep.value && o.dataset.country && o.dataset.country !== dep.value) { return false; }
        return true;
      });
    }
    function label(o) { return o.textContent.trim(); }
    function fire() { sel.dispatchEvent(new Event("change", { bubbles: true })); }
    function showSelected() {
      var o = sel.options[sel.selectedIndex];
      inp.value = (o && o.value) ? label(o) : (hid && hid.value ? hid.value : "");
    }
    function render(q) {
      var nq = norm(q), all = options();
      var items = all.filter(function (o) { return !nq || norm(label(o)).indexOf(nq) > -1; }).slice(0, 100);
      list.innerHTML = ""; active = -1;
      items.forEach(function (o) {
        var li = document.createElement("li"); li.textContent = label(o); li.dataset.v = o.value;
        if (o.value === sel.value) { li.className = "on"; }
        list.appendChild(li);
      });
      var exact = all.some(function (o) { return norm(label(o)) === nq; });
      if (addName && q.trim() && !exact) {
        var add = document.createElement("li"); add.className = "add"; add.dataset.add = q.trim();
        add.textContent = "➕ " + q.trim(); list.appendChild(add);
      }
      if (!list.children.length) {
        var none = document.createElement("li"); none.className = "none"; none.textContent = "—"; list.appendChild(none);
      }
      list.hidden = false;
    }
    function pick(li) {
      if (!li || li.className === "none") { return; }
      if (li.dataset.add !== undefined) {
        sel.value = ""; hid.value = li.dataset.add; inp.value = li.dataset.add;
      } else {
        sel.value = li.dataset.v; if (hid) { hid.value = ""; } showSelected();
      }
      list.hidden = true; fire();
    }
    list.addEventListener("mousedown", function (e) { var li = e.target.closest("li"); if (li) { e.preventDefault(); pick(li); } });
    inp.addEventListener("focus", function () { inp.select(); render(""); });
    inp.addEventListener("input", function () { if (hid) { hid.value = ""; } render(inp.value); });
    inp.addEventListener("keydown", function (e) {
      var items = [].slice.call(list.children);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); if (list.hidden) { render(inp.value); items = [].slice.call(list.children); }
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach(function (li, i) { li.classList.toggle("act", i === active); });
        if (items[active]) { items[active].scrollIntoView({ block: "nearest" }); }
      } else if (e.key === "Enter" && !list.hidden) {
        e.preventDefault(); pick(items[active >= 0 ? active : 0]);
      } else if (e.key === "Escape") { list.hidden = true; }
    });
    inp.addEventListener("blur", function () {
      setTimeout(function () {
        list.hidden = true;
        var q = inp.value.trim();
        if (!q) { sel.value = ""; if (hid) { hid.value = ""; } return; }
        var m = options().filter(function (o) { return norm(label(o)) === norm(q); })[0];
        if (m) { sel.value = m.value; if (hid) { hid.value = ""; } inp.value = label(m); fire(); }
        else if (addName) { sel.value = ""; hid.value = q; }
        else { showSelected(); }
      }, 120);
    });
    if (dep) {
      dep.addEventListener("change", function () {
        var o = sel.options[sel.selectedIndex];
        if (o && o.dataset.country && o.dataset.country !== dep.value) { sel.value = ""; inp.value = ""; if (hid) { hid.value = ""; } fire(); }
      });
    }
    var pre = sel.getAttribute("data-new");
    if (hid && pre && !sel.value) { hid.value = pre; }
    showSelected();
    if (required) { inp.required = true; }
  }
  function init() { document.querySelectorAll("select[data-combo]").forEach(enhance); }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
})();

"""app.css + theme.css + theme2.css -> static/css/site.css (tek istek, kucultulmus).
CSS dosyalarini degistirince calistir:  python tools/build_css.py   (yukle.ps1 de bunu calistirir)"""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent / "static" / "css"
parts = []
for name in ("app.css", "theme.css", "theme2.css"):
    css = (root / name).read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css).strip()
    parts.append(css)
(root / "site.css").write_text("\n".join(parts) + "\n", encoding="utf-8")
print("site.css:", (root / "site.css").stat().st_size, "bayt")

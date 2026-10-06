import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
src = Path(sys.argv[1]); out = Path(sys.argv[2])
footer = ("<div style=\"width:100%;font-size:7px;color:#5a6675;padding:0 14mm;display:flex;justify-content:space-between;"
          "font-family:DejaVu Sans,Arial\"><span>seo-advisor requirements · Gurzu · October 2026</span>"
          "<span>Page <span class='pageNumber'></span> of <span class='totalPages'></span></span></div>")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    pg.goto(src.as_uri()); pg.wait_for_function("window.mermaidDone === true", timeout=60000)
    err = pg.evaluate("window.mermaidError || ''"); print("mermaid error:", err or "none")
    print("svgs:", pg.evaluate("document.querySelectorAll('.diagram svg').length"))
    pg.pdf(path=str(out), format="A4", landscape=False, print_background=True, display_header_footer=True,
           header_template="<div></div>", footer_template=footer,
           margin={"top": "13mm", "bottom": "15mm", "left": "14mm", "right": "14mm"})
    b.close()
print("wrote", out)

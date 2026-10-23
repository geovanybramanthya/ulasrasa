"""check_ringkasan_charts.py - cek terarah teks SVG grafik modul Ringkasan.

Melengkapi font_sweep_svg.py: memastikan grafik Ringkasan benar-benar
sudah ter-render saat disapu (di sapuan 'after' teks SVG-nya belum
muncul di DOM), lalu menghitung Source Sans di teks grafiknya saja.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

SWEEP_SVG_ONLY = """() => {
  const out = [];
  const plots = Array.from(document.querySelectorAll('.js-plotly-plot'));
  for (const el of document.querySelectorAll('body *')) {
    if (!el.closest('svg')) continue;
    if (el.tagName !== 'text') continue;
    const direct = (el.textContent || '').trim();
    if (!direct) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const plot = el.closest('.js-plotly-plot');
    out.push({plot_idx: plot ? plots.indexOf(plot) : -1,
              font: cs.fontFamily, text: direct.slice(0, 60)});
  }
  return out;
}"""


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8517"
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        page.wait_for_function(
            "document.querySelectorAll('.js-plotly-plot svg text').length > 0",
            timeout=90000)
        page.wait_for_timeout(2500)
        els = page.evaluate(SWEEP_SVG_ONLY)
        browser.close()

    ss = [e for e in els if "Source Sans" in e["font"]]
    fonts = Counter(e["font"].split(",")[0].strip().strip('"') for e in els)
    print(f"Ringkasan chart SVG texts: total={len(els)} source_sans={len(ss)} "
          f"by_plot={dict(Counter(e['plot_idx'] for e in ss))} fonts={dict(fonts)}")
    for e in els:
        print(f"  plot {e['plot_idx']} | {e['font'].split(',')[0]:20s} | {e['text']}")
    out = {"module": "Ringkasan", "chart_texts": els, "source_sans": len(ss)}
    with open(os.path.join(HERE, "ringkasan_charts_check.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return 0 if not ss else 1


if __name__ == "__main__":
    sys.exit(main())

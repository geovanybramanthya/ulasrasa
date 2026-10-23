"""font_sweep_svg.py - sapuan computed style font UlasRasa TERMASUK SVG <text>.

Bukti perbaikan D1 putaran 3 (font grafik Plotly modul Rincian): sapuan
gaya auditor putaran 2 - mengukur font-family terhitung (computed)
SETIAP elemen yang memuat teks dan terlihat, termasuk elemen <text>
di dalam SVG grafik Plotly (yang terlewat sapuan HTML putaran 2).
Hasil dirinci per modul dan per grafik (indeks .js-plotly-plot).

Target: NOL elemen teks berisi "Source Sans" di semua modul; label
grafik terukur Inter; label persen donat terukur JetBrains Mono.

Pemakaian (di PC, server Streamlit berjalan):
  py font_sweep_svg.py --url http://localhost:8517 --tag before
Hasil: font_sweep_svg_<tag>.json di folder yang sama + ringkasan stdout.
"""
import argparse
import json
import os
import sys
import traceback
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

SWEEP_JS = """() => {
  const out = [];
  const plots = Array.from(document.querySelectorAll('.js-plotly-plot'));
  const els = Array.from(document.querySelectorAll('body *'));
  for (const el of els) {
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
    const inSvg = !!el.closest('svg');
    let direct = '';
    if (inSvg) {
      // hanya elemen <text> SVG yang dihitung (tspan terbaca via textContent induk)
      if (el.tagName !== 'text') continue;
      direct = (el.textContent || '').trim();
    } else {
      for (const n of el.childNodes) {
        if (n.nodeType === 3) direct += n.textContent;
      }
      direct = direct.trim();
    }
    if (!direct) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    let cls = '';
    try { cls = (typeof el.className === 'string') ? el.className
              : (el.className && el.className.baseVal) || ''; } catch (e) { cls = ''; }
    const plot = el.closest('.js-plotly-plot');
    out.push({
      tag: el.tagName,
      svg: inSvg,
      plot_idx: plot ? plots.indexOf(plot) : -1,
      cls: String(cls).slice(0, 90),
      font: cs.fontFamily,
      text: direct.slice(0, 60)
    });
  }
  return out;
}"""


def primary(font):
    if not font:
        return "(none)"
    return font.split(",")[0].strip().strip('"').strip("'")


def goto_module(page, name, marker, timeout=90000):
    page.locator('[data-testid="stButtonGroup"] button', has_text=name).first.click()
    page.get_by_text(marker, exact=False).first.wait_for(timeout=timeout)
    page.wait_for_timeout(2000)


def sweep_module(page, label):
    els = page.evaluate(SWEEP_JS)
    fonts = Counter(primary(e["font"]) for e in els)
    ss = [e for e in els if "Source Sans" in e["font"]]
    ss_by_plot = Counter(e["plot_idx"] for e in ss if e["svg"])
    chart_texts = [e for e in els if e["svg"]]
    return {"label": label, "total_text_elements": len(els),
            "chart_text_elements": len(chart_texts),
            "by_primary_font": dict(fonts),
            "source_sans_count": len(ss),
            "source_sans_by_plot": {str(k): v for k, v in sorted(ss_by_plot.items())},
            "source_sans_elements": ss,
            "chart_text_samples": chart_texts[:80],
            "elements": els}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8517")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    result = {"url": args.url, "tag": args.tag, "modules": []}
    out_path = os.path.join(HERE, f"font_sweep_svg_{args.tag}.json")

    def flush():
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        page.wait_for_timeout(3000)

        result["modules"].append(sweep_module(page, "Ringkasan"))
        flush()

        goto_module(page, "Rincian Aspek", "Pilih aspek")
        # tunggu ketiga grafik Rincian selesai render
        page.wait_for_function(
            "document.querySelectorAll('.js-plotly-plot').length >= 3",
            timeout=60000)
        page.wait_for_timeout(2000)
        result["modules"].append(sweep_module(page, "Rincian"))
        flush()

        goto_module(page, "Rencana Aksi", "Akar Masalah")
        page.wait_for_timeout(1500)
        result["modules"].append(sweep_module(page, "Rencana"))
        flush()

        goto_module(page, "Coba Ulasan", "Tulis Ulasan Pelanggan")
        result["modules"].append(sweep_module(page, "Coba (awal)"))
        flush()
        try:
            ta = page.locator('[data-testid="stTextArea"] textarea').first
            ta.fill("Nasi gorengnya enak banget dan bumbunya meresap, "
                    "tapi kemasannya bocor parah sampai minyak tumpah kemana-mana.")
            page.locator('button', has_text="Analisis Ulasan").first.click()
            page.get_by_text("Hasil Analisis", exact=False).first.wait_for(timeout=90000)
            page.wait_for_timeout(2000)
            result["modules"].append(sweep_module(page, "Coba (hasil)"))
        except Exception as ex:
            result["coba_run_error"] = f"{type(ex).__name__}: {ex}"
        flush()

        ctx.close()
        browser.close()

    flush()
    for m in result["modules"]:
        print(f"{m['label']:16s} total={m['total_text_elements']:4d} "
              f"chart_text={m['chart_text_elements']:3d} "
              f"source_sans={m['source_sans_count']:3d} "
              f"by_plot={m['source_sans_by_plot']} fonts={m['by_primary_font']}")
    if "coba_run_error" in result:
        print("COBA RUN ERROR:", result["coba_run_error"])
    total_ss = sum(m["source_sans_count"] for m in result["modules"])
    print(f"TOTAL Source Sans ({args.tag}): {total_ss}")
    print(f"JSON -> {out_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

"""font_sweep.py - sapuan computed style font menyeluruh 4 modul UlasRasa.

Bukti perbaikan D1 putaran 2 (defect font): mengukur font-family terhitung
(computed) SETIAP elemen HTML yang memuat teks langsung dan terlihat, di
keempat modul. Target: NOL elemen teks berisi "Source Sans".

Pemakaian (di PC, server Streamlit berjalan):
  py font_sweep.py --tag before
  py font_sweep.py --tag after
Hasil: font_sweep_<tag>.json di folder yang sama + ringkasan di stdout.
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
  const els = Array.from(document.querySelectorAll('body *'));
  for (const el of els) {
    if (el.closest('svg')) continue;
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
    let direct = '';
    for (const n of el.childNodes) {
      if (n.nodeType === 3) direct += n.textContent;
    }
    direct = direct.trim();
    if (!direct) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    let cls = '';
    try { cls = (typeof el.className === 'string') ? el.className : ''; } catch (e) { cls = ''; }
    out.push({
      tag: el.tagName,
      cls: cls.slice(0, 90),
      testid: el.getAttribute('data-testid') || '',
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
    return {"label": label, "total_text_elements": len(els),
            "by_primary_font": dict(fonts),
            "source_sans_count": len(ss), "source_sans_elements": ss,
            "elements": els}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8516")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    result = {"url": args.url, "tag": args.tag, "modules": []}
    out_path = os.path.join(HERE, f"font_sweep_{args.tag}.json")

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
        result["modules"].append(sweep_module(page, "Rincian"))
        flush()

        goto_module(page, "Rencana Aksi", "Akar Masalah")
        page.wait_for_timeout(1500)
        result["modules"].append(sweep_module(page, "Rencana"))
        flush()

        goto_module(page, "Coba Ulasan", "Tulis Ulasan Pelanggan")
        result["modules"].append(sweep_module(page, "Coba (awal)"))
        flush()
        # jalankan satu analisis agar baris hasil + status ikut tersapu
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

        # sampel peran font lain (dari modul terakhir yang aktif)
        result["role_samples"] = page.evaluate("""() => {
          const pick = (sel) => { const el = document.querySelector(sel);
            return el ? {font: getComputedStyle(el).fontFamily, text: (el.textContent||'').trim().slice(0,50)} : null; };
          return {
            greeting_jakarta: pick('.greeting'),
            kpi_value_mono: pick('.kpi-value'),
            stat_value_mono: pick('.stat-value'),
            card_title_jakarta: pick('.card-title'),
            button_label_jakarta: pick('.stButton [data-testid="stMarkdownContainer"] p'),
            first_paragraph: pick('[data-testid="stMarkdownContainer"] p'),
            card_sub: pick('.card-sub'),
            stat_label: pick('.stat-label'),
            brand_sub: pick('.brand-sub')
          };
        }""")
        ctx.close()
        browser.close()

    flush()
    for m in result["modules"]:
        print(f"{m['label']:16s} total={m['total_text_elements']:4d} "
              f"source_sans={m['source_sans_count']:3d} fonts={m['by_primary_font']}")
    print("role_samples:", json.dumps(result["role_samples"], ensure_ascii=False))
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

"""capture.py - tangkapan layar bukti UI UlasRasa (Playwright, PRD Bag. 5).

Ditulis di docs/ui-evidence/ di repo dan dipakai semua tahap.

Contoh:
  py capture.py --url http://localhost:8510 --out tahap-0/ringkasan-awal-desktop.png \
      --width 1440 --height 900 --wait-text "Ringkasan Kesehatan Dapur"
  py capture.py ... --click-text "2. Deep-Dive Aspek" --wait-text "Deep-Dive Analisis" ...
  py capture.py ... --full-page

Argumen:
  --url          URL aplikasi (server Streamlit terpisah)
  --out          path PNG relatif terhadap docs/ui-evidence/
  --width/--height  viewport (default 1440x900)
  --wait-text    teks penanda render yang ditunggu (timeout 60 dtk)
  --click-text   teks elemen yang diklik sebelum tangkap (boleh diulang)
  --settle-ms    jeda stabil setelah penanda (default 2000)
  --full-page    tangkap satu halaman penuh
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--wait-text", default=None)
    ap.add_argument("--click-text", action="append", default=[])
    ap.add_argument("--settle-ms", type=int, default=2000)
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--touch", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    out_path = os.path.join(HERE, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=1,
            has_touch=args.touch,
            is_mobile=args.touch,
        )
        page = ctx.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        if args.wait_text:
            page.get_by_text(args.wait_text, exact=False).first.wait_for(timeout=60000)
        for txt in args.click_text:
            page.get_by_text(txt, exact=False).first.click()
            page.wait_for_timeout(1200)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
        page.wait_for_timeout(args.settle_ms)
        page.screenshot(path=out_path, full_page=args.full_page)
        browser.close()
    print(f"CAPTURED {out_path} ({args.width}x{args.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

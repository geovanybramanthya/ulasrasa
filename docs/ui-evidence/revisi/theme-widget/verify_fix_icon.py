"""Verifikasi perbaikan ikon uploader + probe checkbox Rencana (observasi)."""
import json, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "http://localhost:8531"
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_text("Pilih restoran", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)
    page.locator('button', has_text="Masuk Dashboard").first.click()
    page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)
    page.locator('button', has_text="Ganti Data").first.click()
    page.wait_for_timeout(2500)
    page.locator('[data-testid="stRadio"] label', has_text="Upload Dataset").first.click()
    page.wait_for_timeout(2500)
    res["dropzone_icon"] = page.evaluate("""() => {
      const ic = document.querySelector('[data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"]');
      const ub = document.querySelector('[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]');
      return {icon_font: ic ? getComputedStyle(ic).fontFamily : null,
              icon_text: ic ? ic.textContent.trim() : null,
              btn_bg: ub ? getComputedStyle(ub).backgroundColor : null,
              btn_radius: ub ? getComputedStyle(ub).borderRadius : null};
    }""")
    dz = page.locator('[data-testid="stFileUploaderDropzone"]')
    dz.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    box = dz.bounding_box()
    if box:
        page.screenshot(path=os.path.join(HERE, "after-dropzone-fix.png"),
                        clip={"x": max(box["x"] - 8, 0), "y": max(box["y"] - 8, 0),
                              "width": box["width"] + 16, "height": box["height"] + 16})
    # observasi checkbox di Rencana
    page.locator('[data-testid="stButtonGroup"] button', has_text="Rencana").first.click()
    page.wait_for_timeout(3000)
    res["rencana_checkbox"] = page.evaluate("""() => {
      const boxes = Array.from(document.querySelectorAll('[data-testid="stCheckbox"] label')).slice(0, 3);
      return boxes.map(lab => {
        const input = lab.querySelector('input');
        const first = lab.querySelector(':scope > *');
        const cs = first ? getComputedStyle(first) : null;
        return {text: lab.textContent.trim().slice(0, 30),
                checked: input ? input.checked : null,
                first_tag: first ? first.tagName : null,
                first_bg: cs ? cs.backgroundColor : null};
      });
    }""")
    res["rencana_sweep_ss"] = page.evaluate("""() => {
      let n = 0, tot = 0;
      for (const el of document.querySelectorAll('body *')) {
        if (el.closest('svg')) continue;
        let direct = '';
        for (const nd of el.childNodes) if (nd.nodeType === 3) direct += nd.textContent;
        if (!direct.trim()) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        tot++;
        if (cs.fontFamily.includes('Source Sans')) n++;
      }
      return {total: tot, source_sans: n};
    }""")
    ctx.close()
    b.close()
out = os.path.join(HERE, "fix_icon.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print("JSON ->", out)

"""verify_widget.py v2 - verifikasi paket T (widget + kelas landing).

Alur aplikasi revisi landing: landing akun demo -> Masuk Dashboard ->
dashboard (top bar 4 kolom) -> modul Rincian (filter selectbox) -> kembali
Ringkasan -> Panel Ganti Data.

Keadaan bukti:
 (L)   landing desktop 1440x900 + mobile 390px: kartu akun putih radius 20,
       panel visual + kartu kaca menimpa gambar, angka KHS Mono.
 (i)   popover selectbox TERBUKA di Rincian: item Inter, radius/bayangan,
       tinta hover pastel + terpilih tegas (computed).
 (ii)  Panel Ganti Data + expander TERBUKA: sapuan panel 0 Source Sans,
       radio hijau, uploader/alert/expander/input terukur.
 (iii) Regresi D1/D2: top bar fixed sesudah scroll, sapaan Jakarta, KPI Mono,
       sapuan Ringkasan 0 Source Sans, tombol primer gradien hijau,
       top bar 4 kolom tidak menutupi konten (desktop + 390px).

Hasil: widget_after.json + screenshot di folder yang sama.
"""
import json, os, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "http://localhost:8531"

SWEEP_JS = """(root) => {
  const out = [];
  for (const el of root.querySelectorAll('*')) {
    if (el.closest('svg')) continue;
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
    let direct = '';
    for (const n of el.childNodes) if (n.nodeType === 3) direct += n.textContent;
    direct = direct.trim();
    if (!direct) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    out.push({tag: el.tagName, testid: el.getAttribute('data-testid') || '',
              font: cs.fontFamily, text: direct.slice(0, 50)});
  }
  return out;
}"""

LANDING_JS = """() => {
  const out = {};
  const card = document.querySelector('div[class*="st-key-landing_acct_"]');
  if (card) { const cs = getComputedStyle(card);
    out.acct_card = {bg: cs.backgroundColor, radius: cs.borderRadius, shadow: cs.boxShadow,
      border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor, padding: cs.padding}; }
  const vis = document.querySelector('div.st-key-landing_visual');
  if (vis) { const cs = getComputedStyle(vis);
    out.visual = {bg: cs.backgroundColor, radius: cs.borderRadius, padding: cs.padding, marginTop: cs.marginTop}; }
  const img = document.querySelector('div.st-key-landing_visual img');
  if (img) { const r = img.getBoundingClientRect();
    out.img = {radius: getComputedStyle(img).borderRadius, top: r.top, bottom: r.bottom}; }
  const glass = document.querySelector('.landing-glass');
  if (glass) { const cs = getComputedStyle(glass); const r = glass.getBoundingClientRect();
    out.glass = {bg: cs.backgroundColor, radius: cs.borderRadius, position: cs.position,
      marginTop: cs.marginTop, top: r.top, bottom: r.bottom,
      backdrop: cs.backdropFilter || cs.webkitBackdropFilter || ''}; }
  if (out.img && out.glass) out.glass_overlaps_img = out.glass.top < out.img.bottom;
  const num = document.querySelector('.landing-khs-num');
  if (num) { const cs = getComputedStyle(num);
    out.khs_num = {font: cs.fontFamily, size: cs.fontSize, weight: cs.fontWeight}; }
  const mbc = document.querySelector('[data-testid="stMainBlockContainer"]');
  if (mbc) out.main_padding_top = getComputedStyle(mbc).paddingTop;
  const first = document.querySelector('.brand-lockup');
  if (first) out.first_content_top = first.getBoundingClientRect().top;
  return out;
}"""

def enter_dashboard(page):
    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_text("Pilih restoran", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)
    page.locator('button', has_text="Masuk Dashboard").first.click()
    page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)

def main():
    from playwright.sync_api import sync_playwright
    res = {}
    def flush():
        with open(os.path.join(HERE, "widget_after.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)

    with sync_playwright() as p:
        b = p.chromium.launch()

        # ---------- (L) landing desktop ----------
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.get_by_text("Pilih restoran", exact=False).first.wait_for(timeout=120000)
        page.wait_for_timeout(3000)
        res["landing_desktop"] = page.evaluate(LANDING_JS)
        page.screenshot(path=os.path.join(HERE, "after-landing-desktop.png"))
        flush()

        # ---------- masuk dashboard ----------
        page.locator('button', has_text="Masuk Dashboard").first.click()
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        page.wait_for_timeout(3000)

        # ---------- (iii) regresi dasar + top bar 4 kolom ----------
        els = page.evaluate(f"() => {{ const r = document.querySelector('[data-testid=\"stAppViewContainer\"]') || document.body; return ({SWEEP_JS})(r); }}")
        ss = [e for e in els if "Source Sans" in e["font"]]
        res["ringkasan_sweep"] = {"total": len(els), "source_sans": len(ss), "ss_samples": ss[:5]}
        res["roles_topbar"] = page.evaluate("""() => {
          const pick = (sel) => { const el = document.querySelector(sel);
            return el ? getComputedStyle(el).fontFamily : null; };
          const tb = document.querySelector('div.st-key-topbar');
          const gr = document.querySelector('.greeting');
          const ga = document.querySelector('div.st-key-topbar [data-testid="stButton"] button');
          const mbc = document.querySelector('[data-testid="stMainBlockContainer"]');
          return {greeting: pick('.greeting'), kpi_value: pick('.kpi-value'),
                  card_title: pick('.card-title'),
                  topbar_position: tb ? getComputedStyle(tb).position : null,
                  topbar_top: tb ? tb.getBoundingClientRect().top : null,
                  topbar_bottom: tb ? tb.getBoundingClientRect().bottom : null,
                  topbar_height: tb ? tb.getBoundingClientRect().height : null,
                  greeting_top: gr ? gr.getBoundingClientRect().top : null,
                  main_padding_top: mbc ? getComputedStyle(mbc).paddingTop : null,
                  ganti_akun_btn: ga ? {marginTop: getComputedStyle(ga).marginTop,
                    whiteSpace: getComputedStyle(ga).whiteSpace,
                    text: ga.textContent.trim().slice(0, 20)} : null};
        }""")
        page.evaluate("() => window.scrollTo(0, 1400)")
        page.wait_for_timeout(900)
        res["scroll_test"] = page.evaluate("""() => {
          const tb = document.querySelector('div.st-key-topbar');
          return {scrollY: window.scrollY,
                  topbar_top_after: tb ? tb.getBoundingClientRect().top : null,
                  topbar_position: tb ? getComputedStyle(tb).position : null};
        }""")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        flush()

        # ---------- (i) popover di Rincian ----------
        page.locator('[data-testid="stButtonGroup"] button', has_text="Rincian").first.click()
        page.get_by_text("Pilih aspek", exact=False).first.wait_for(timeout=90000)
        page.wait_for_timeout(2500)
        page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        res["select_closed_rincian"] = page.evaluate("""() => {
          const ctl = document.querySelector('[data-testid="stSelectbox"] [data-baseweb="select"] > div');
          if (!ctl) return null; const cs = getComputedStyle(ctl);
          return {bg: cs.backgroundColor, radius: cs.borderRadius,
            border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor, color: cs.color};
        }""")
        page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.click()
        page.wait_for_timeout(1500)
        res["popover"] = page.evaluate("""() => {
          const pop = document.querySelector('[data-baseweb="popover"]');
          if (!pop) return {present: false};
          const body = pop.querySelector(':scope > div');
          const ul = pop.querySelector('ul');
          const bcs = body ? getComputedStyle(body) : null;
          const items = Array.from(pop.querySelectorAll('li[role="option"]')).map(li => {
            const inner = li.querySelector(':scope > div');
            const cs = getComputedStyle(li);
            const ics = inner ? getComputedStyle(inner) : null;
            return {text: li.textContent.trim().slice(0, 40),
                    ariaSelected: li.getAttribute('aria-selected'),
                    li_font: cs.fontFamily, li_color: cs.color, li_padding: cs.padding,
                    inner_bg: ics ? ics.backgroundColor : null,
                    inner_padding: ics ? ics.padding : null,
                    inner_radius: ics ? ics.borderRadius : null,
                    inner_weight: ics ? ics.fontWeight : null};
          });
          return {present: true,
                  body_radius: bcs ? bcs.borderRadius : null,
                  body_shadow: bcs ? bcs.boxShadow : null,
                  ul_radius: ul ? getComputedStyle(ul).borderRadius : null,
                  items};
        }""")
        items_loc = page.locator('[data-baseweb="popover"] li[role="option"]')
        hover_idx = None
        for i in range(items_loc.count()):
            if items_loc.nth(i).get_attribute("aria-selected") != "true":
                hover_idx = i
                break
        if hover_idx is not None:
            items_loc.nth(hover_idx).hover()
            page.wait_for_timeout(700)
            res["popover_hover"] = page.evaluate("""(idx) => {
              const lis = document.querySelectorAll('[data-baseweb="popover"] li[role="option"]');
              const li = lis[idx];
              const inner = li.querySelector(':scope > div');
              return {text: li.textContent.trim().slice(0, 40),
                      inner_bg: inner ? getComputedStyle(inner).backgroundColor : null};
            }""", hover_idx)
        box = page.locator('[data-baseweb="popover"]').bounding_box()
        page.screenshot(path=os.path.join(HERE, "after-popover-open.png"))
        if box:
            page.screenshot(path=os.path.join(HERE, "after-popover-clip.png"),
                            clip={"x": max(box["x"] - 10, 0), "y": max(box["y"] - 10, 0),
                                  "width": box["width"] + 20, "height": box["height"] + 20})
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        flush()

        # ---------- (ii) Panel Ganti Data + expander ----------
        page.locator('[data-testid="stButtonGroup"] button', has_text="Ringkasan").first.click()
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=90000)
        page.wait_for_timeout(2000)
        page.locator('button', has_text="Ganti Data").first.click()
        page.wait_for_timeout(2500)
        res["radio"] = page.evaluate("""() => {
          return Array.from(document.querySelectorAll('[data-testid="stRadio"] label')).filter(l => l.querySelector('input')).map(lab => {
            const outer = lab.querySelector(':scope > div');
            const dot = outer ? outer.querySelector(':scope > div') : null;
            return {text: lab.textContent.trim().slice(0, 30),
                    checked: lab.querySelector('input').checked,
                    outer_bg: outer ? getComputedStyle(outer).backgroundColor : null,
                    dot_bg: dot ? getComputedStyle(dot).backgroundColor : null};
          });
        }""")
        page.locator('[data-testid="stExpander"] summary').first.click()
        page.wait_for_timeout(1500)
        res["expander_form"] = page.evaluate("""() => {
          const out = {};
          const tp = document.querySelector('[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p');
          out.summary_font_p = tp ? getComputedStyle(tp).fontFamily : null;
          const d = document.querySelector('[data-testid="stExpander"] details');
          if (d) { const cs = getComputedStyle(d);
            out.details = {radius: cs.borderRadius, border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor}; }
          const ta = document.querySelector('[data-testid="stTextAreaRootElement"]');
          if (ta) { const cs = getComputedStyle(ta);
            out.textarea_root = {bg: cs.backgroundColor, radius: cs.borderRadius,
              border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor, shadow: cs.boxShadow}; }
          const ti = document.querySelector('[data-testid="stTextInputRootElement"]');
          if (ti) { const cs = getComputedStyle(ti);
            out.textinput_root = {bg: cs.backgroundColor, radius: cs.borderRadius,
              border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor, shadow: cs.boxShadow}; }
          const btn = document.querySelector('[data-testid="stExpander"] button[kind="primary"]');
          if (btn) { const cs = getComputedStyle(btn);
            out.primary_btn = {bgImage: cs.backgroundImage, color: cs.color, font: cs.fontFamily, radius: cs.borderRadius, text: btn.textContent.trim().slice(0, 40)}; }
          return out;
        }""")
        page.locator('[data-testid="stTextArea"] textarea').first.click()
        page.wait_for_timeout(600)
        res["textarea_focus"] = page.evaluate("""() => {
          const ta = document.querySelector('[data-testid="stTextAreaRootElement"]');
          if (!ta) return null; const cs = getComputedStyle(ta);
          return {borderColor: cs.borderTopColor, shadow: cs.boxShadow};
        }""")
        panel = page.evaluate(f"() => {{ const r = document.querySelector('.st-key-paneldata'); return r ? ({SWEEP_JS})(r) : null; }}")
        if panel is not None:
            pss = [e for e in panel if "Source Sans" in e["font"]]
            res["panel_sweep_preset_mode"] = {"total": len(panel), "source_sans": len(pss), "ss_samples": pss[:5]}
        page.locator('.st-key-paneldata').scroll_into_view_if_needed()
        page.wait_for_timeout(700)
        page.screenshot(path=os.path.join(HERE, "after-panel-expander-open.png"))
        flush()

        # mode unggah
        page.locator('[data-testid="stRadio"] label', has_text="Upload Dataset").first.click()
        page.wait_for_timeout(2500)
        res["upload_mode"] = page.evaluate("""() => {
          const out = {};
          const dz = document.querySelector('[data-testid="stFileUploaderDropzone"]');
          if (dz) { const cs = getComputedStyle(dz);
            out.dropzone = {border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor,
              radius: cs.borderRadius, bg: cs.backgroundColor}; }
          const ins = document.querySelector('[data-testid="stFileUploaderDropzoneInstructions"] span, [data-testid="stFileUploaderDropzoneInstructions"] div');
          if (ins) out.instructions_font = getComputedStyle(ins).fontFamily;
          const ub = document.querySelector('[data-testid="stFileUploader"] button');
          if (ub) { const cs = getComputedStyle(ub);
            const pp = ub.querySelector('[data-testid="stMarkdownContainer"] p');
            out.upload_btn = {bg: cs.backgroundColor, radius: cs.borderRadius, color: cs.color,
              border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor,
              label_font: pp ? getComputedStyle(pp).fontFamily : null, text: ub.textContent.trim().slice(0, 20)}; }
          const ac = document.querySelector('[data-testid="stAlertContainer"]');
          if (ac) { const cs = getComputedStyle(ac);
            const ap = document.querySelector('[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p');
            out.alert = {radius: cs.borderRadius, bg: cs.backgroundColor, container_font: cs.fontFamily,
              text_font: ap ? getComputedStyle(ap).fontFamily : null,
              text: ap ? ap.textContent.trim().slice(0, 50) : null}; }
          return out;
        }""")
        panel2 = page.evaluate(f"() => {{ const r = document.querySelector('.st-key-paneldata'); return r ? ({SWEEP_JS})(r) : null; }}")
        if panel2 is not None:
            pss2 = [e for e in panel2 if "Source Sans" in e["font"]]
            res["panel_sweep_upload_mode"] = {"total": len(panel2), "source_sans": len(pss2), "ss_samples": pss2[:5]}
        page.locator('.st-key-paneldata').scroll_into_view_if_needed()
        page.wait_for_timeout(700)
        page.screenshot(path=os.path.join(HERE, "after-panel-upload-mode.png"))
        flush()
        ctx.close()

        # ---------- (L) landing mobile 390 + dashboard mobile top bar ----------
        ctxm = b.new_context(viewport={"width": 390, "height": 844})
        pm = ctxm.new_page()
        pm.goto(URL, wait_until="domcontentloaded")
        pm.get_by_text("Pilih restoran", exact=False).first.wait_for(timeout=120000)
        pm.wait_for_timeout(3000)
        res["landing_mobile"] = pm.evaluate(LANDING_JS)
        pm.screenshot(path=os.path.join(HERE, "after-landing-mobile.png"))
        pm.locator('button', has_text="Masuk Dashboard").first.click()
        pm.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        pm.wait_for_timeout(3000)
        res["dashboard_mobile_topbar"] = pm.evaluate("""() => {
          const tb = document.querySelector('div.st-key-topbar');
          const gr = document.querySelector('.greeting');
          const mbc = document.querySelector('[data-testid="stMainBlockContainer"]');
          return {topbar_top: tb ? tb.getBoundingClientRect().top : null,
                  topbar_bottom: tb ? tb.getBoundingClientRect().bottom : null,
                  topbar_height: tb ? tb.getBoundingClientRect().height : null,
                  greeting_top: gr ? gr.getBoundingClientRect().top : null,
                  main_padding_top: mbc ? getComputedStyle(mbc).paddingTop : null};
        }""")
        pm.screenshot(path=os.path.join(HERE, "after-dashboard-mobile-topbar.png"))
        flush()
        ctxm.close()
        b.close()

    print(json.dumps(res, ensure_ascii=False, indent=1)[:7000])
    print("JSON ->", os.path.join(HERE, "widget_after.json"))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

"""_revisi_common.py - helper bersama harness verifikasi Revisi Mayor UI.

Dipakai oleh font_sweep_open_states.py, account_parity.py, dan
journey_revisi.py di folder ini (docs/ui-evidence/revisi/). Mengikuti pola
bukti lama (audit-fix2/font_sweep.py, audit-fix3/font_sweep_svg.py,
start_server.ps1): server Streamlit detached di port bebas, render penuh
ditunggu (muat model IndoBERT +/-18-30 detik), hasil ditulis sebagai JSON
di folder ini.

BASELINE di bawah disalin persis dari docs/ui-evidence/baseline.json
(teraudit) - JANGAN diubah tanpa memperbarui baseline.json:
  Semua Outlet (Benchmark)        KHS 67.27  WASPADA (Perhatian)   n=100
  Ayam Geprek Sambal Korek Barokah 55.84  KRITIS (Audit Segera)  n=25
  Bakso Rusuk Solo Pak Ndut        68.24  WASPADA (Perhatian)   n=25
  Bebek Goreng Madura Cak Roni     83.00  PRIMA (Optimal)       n=25
  Kopi Susu Senja & Toast          59.55  KRITIS (Audit Segera)  n=25
Catatan tampilan: hero/KPI app menampilkan KHS 1 desimal ("55.8%"),
jadi perbandingan angka memakai nilai terbulatkan 1 desimal dari kedua
sisi + kata status (WASPADA/KRITIS/PRIMA).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_PORT = 8525
DEFAULT_URL = f"http://localhost:{DEFAULT_PORT}"

AYAM = "Ayam Geprek Sambal Korek Barokah"
BAKSO = "Bakso Rusuk Solo Pak Ndut"
BEBEK = "Bebek Goreng Madura Cak Roni"
KOPI = "Kopi Susu Senja & Toast"
BENCH_GREETING = "Semua Outlet"
BENCH_LABEL = "Semua Outlet (Benchmark Industri)"

# key = nama sapaan di dashboard; card_labels = teks yang mungkin tampil
# di kartu landing untuk akun itu (dicoba berurutan).
BASELINE = {
    BENCH_GREETING: {
        "khs": 67.27, "status_word": "WASPADA",
        "status_label": "WASPADA (Perhatian)", "n_reviews": 100,
        "card_labels": [BENCH_LABEL, "Semua Outlet", "Benchmark Industri", "Benchmark"],
    },
    AYAM: {
        "khs": 55.84, "status_word": "KRITIS",
        "status_label": "KRITIS (Audit Segera)", "n_reviews": 25,
        "card_labels": [AYAM],
    },
    BAKSO: {
        "khs": 68.24, "status_word": "WASPADA",
        "status_label": "WASPADA (Perhatian)", "n_reviews": 25,
        "card_labels": [BAKSO],
    },
    BEBEK: {
        "khs": 83.00, "status_word": "PRIMA",
        "status_label": "PRIMA (Optimal)", "n_reviews": 25,
        "card_labels": [BEBEK],
    },
    KOPI: {
        "khs": 59.55, "status_word": "KRITIS",
        "status_label": "KRITIS (Audit Segera)", "n_reviews": 25,
        "card_labels": [KOPI],
    },
}
ACCOUNT_ORDER = [AYAM, BAKSO, BEBEK, KOPI, BENCH_GREETING]


# ------------------------------------------------------------------ server
def _health(url, timeout=3):
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/_stcore/health",
                                    timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_server(url=DEFAULT_URL, log_name="server_revisi.log"):
    """Pastikan server Streamlit hidup di url. Bila belum, start detached
    (pola start_server.ps1 lama, tapi dari Python) dan tunggu health.

    Mengembalikan (started_by_us: bool, pid: int|None).
    """
    if _health(url):
        return False, None
    port = int(url.rsplit(":", 1)[-1].split("/")[0])
    log_path = os.path.join(HERE, log_name)
    logf = open(log_path, "ab")
    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.port", str(port), "--server.headless", "true",
         "--browser.gatherUsageStats", "false"],
        cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT,
        creationflags=flags, close_fds=True,
    )
    deadline = time.time() + 240
    while time.time() < deadline:
        if _health(url):
            return True, proc.pid
        if proc.poll() is not None:
            raise RuntimeError(
                f"server Streamlit mati saat start (exit {proc.returncode}); "
                f"lihat {log_path}")
        time.sleep(2)
    raise RuntimeError(f"server tidak sehat dalam 240 dtk di {url}")


def stop_server(pid):
    if not pid:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True)
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


# ------------------------------------------------------------------ sapuan font
# JS identik pendekatannya dengan audit-fix3/font_sweep_svg.py SWEEP_JS:
# semua elemen teks terlihat, termasuk <text> di SVG Plotly.
SWEEP_JS = """() => {
  const out = [];
  const plots = Array.from(document.querySelectorAll('.js-plotly-plot'));
  const els = Array.from(document.querySelectorAll('body *'));
  for (const el of els) {
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
    const inSvg = !!el.closest('svg');
    let direct = '';
    if (inSvg) {
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
      testid: el.getAttribute('data-testid') || '',
      font: cs.fontFamily,
      text: direct.slice(0, 60)
    });
  }
  return out;
}"""

ROLE_JS = """() => {
  const pick = (sel) => { const el = document.querySelector(sel);
    return el ? {font: getComputedStyle(el).fontFamily,
                 text: (el.textContent||'').trim().slice(0,50)} : null; };
  return {
    greeting_jakarta: pick('.greeting'),
    hero_status_jakarta: pick('.hero-status'),
    card_title_jakarta: pick('.card-title'),
    kpi_value_mono: pick('.kpi-value'),
    stat_value_mono: pick('.stat-value'),
    num_mono: pick('.num'),
    first_paragraph: pick('[data-testid="stMarkdownContainer"] p'),
    card_sub: pick('.card-sub'),
    brand_name_jakarta: pick('.brand-name')
  };
}"""


def primary(font):
    if not font:
        return "(none)"
    return font.split(",")[0].strip().strip('"').strip("'")


def sweep(page, label):
    els = page.evaluate(SWEEP_JS)
    fonts = Counter(primary(e["font"]) for e in els)
    ss = [e for e in els if "Source Sans" in e["font"]]
    return {"label": label, "total_text_elements": len(els),
            "chart_text_elements": len([e for e in els if e["svg"]]),
            "by_primary_font": dict(fonts),
            "source_sans_count": len(ss),
            "violations": ss,
            "role_samples": page.evaluate(ROLE_JS),
            "elements": els}


def role_verdicts(role_samples):
    """Cek peran font dari sampel: sapaan/judul -> Jakarta, angka -> Mono."""
    out = {}
    checks = {
        "greeting_jakarta": "Plus Jakarta Sans",
        "hero_status_jakarta": "Plus Jakarta Sans",
        "card_title_jakarta": "Plus Jakarta Sans",
        "brand_name_jakarta": "Plus Jakarta Sans",
        "kpi_value_mono": "JetBrains Mono",
        "stat_value_mono": "JetBrains Mono",
        "num_mono": "JetBrains Mono",
    }
    for key, expect in checks.items():
        s = (role_samples or {}).get(key)
        if s is None:
            out[key] = {"expected": expect, "found": None, "ok": None,
                        "note": "elemen tidak ada di keadaan ini"}
        else:
            out[key] = {"expected": expect, "found": s["font"],
                        "text": s["text"], "ok": expect in s["font"]}
    return out


# ------------------------------------------------------------------ baca DOM
HERO_JS = """() => {
  const q = (sel) => { const el = document.querySelector(sel);
    return el ? (el.textContent || '').trim() : null; };
  const kpis = Array.from(document.querySelectorAll('.kpi-value'))
    .map(e => (e.textContent || '').trim());
  return {
    greeting: q('.greeting'),
    hero_status: q('.hero-status'),
    kpi_values: kpis,
    kpi_micro0: (() => { const el = document.querySelector('.kpi-micro');
      return el ? (el.textContent || '').trim() : null; })(),
    body_has_halo: (document.body.innerText || '').includes('Halo,')
  };
}"""


def read_hero(page):
    """Baca sapaan + KHS + status + total ulasan dari hero Ringkasan."""
    d = page.evaluate(HERO_JS)
    khs = None
    total = None
    if d.get("kpi_values"):
        try:
            khs = float(d["kpi_values"][0].replace("%", "").replace(",", ".").strip())
        except Exception:
            khs = None
        try:
            total = int("".join(ch for ch in d["kpi_values"][1] if ch.isdigit()))
        except Exception:
            total = None
    status_text = d.get("hero_status") or d.get("kpi_micro0") or ""
    return {"greeting": d.get("greeting"), "khs_display_1dp": khs,
            "kpi_values": d.get("kpi_values"), "status_text": status_text,
            "total_reviews": total}


def khs_matches(observed_1dp, expected_2dp):
    """Tampilan app 1 desimal; cocok bila pembulatan 1 desimal sama."""
    if observed_1dp is None:
        return False
    return abs(round(float(observed_1dp), 1) - round(float(expected_2dp), 1)) < 0.051


LANDING_JS = """() => {
  const txt = document.body.innerText || '';
  const names = ["Ayam Geprek Sambal Korek Barokah", "Bakso Rusuk Solo Pak Ndut",
    "Bebek Goreng Madura Cak Roni", "Kopi Susu Senja & Toast",
    "Semua Outlet (Benchmark Industri)"];
  const mentions = {};
  for (const n of names) mentions[n] = txt.split(n).length - 1;
  const cards = Array.from(document.querySelectorAll('[class*="st-key-landing_acct"]'));
  return {
    has_greeting_div: !!document.querySelector('.greeting'),
    greeting_text: (() => { const g = document.querySelector('.greeting');
      return g ? (g.textContent || '').trim() : null; })(),
    has_kpi: !!document.querySelector('.kpi-value'),
    has_landing_cards: cards.length > 0,
    landing_card_count: cards.length,
    has_landing_title: txt.includes('Pilih restoran untuk masuk ke dashboard'),
    has_topbar: !!document.querySelector('.brand-name'),
    has_ganti_akun: txt.includes('Ganti Akun'),
    has_ganti_data: txt.includes('Ganti Data'),
    has_module_pills: !!document.querySelector('[data-testid="stButtonGroup"]'),
    resto_mentions: mentions,
    body_excerpt: txt.slice(0, 600)
  };
}"""


def detect_landing(page):
    """Deteksi landing sesuai implementasi final (module_landing.py):
    kartu akun adalah kontainer Streamlit berkelas st-key-landing_acct_*
    dan judulnya "Pilih restoran untuk masuk ke dashboard" (di div
    .greeting - PERHATIAN: landing pun memakai kelas .greeting, jadi
    pembeda dashboard adalah adanya .kpi-value, bukan .greeting).

    Mengembalikan dict mentah LANDING_JS + verdict landing_likely.
    """
    d = page.evaluate(LANDING_JS)
    distinct_visible = sum(1 for v in d["resto_mentions"].values() if v > 0)
    d["distinct_resto_names_visible"] = distinct_visible
    d["landing_likely"] = bool(
        (d["has_landing_cards"] or d["has_landing_title"])
        and not d["has_kpi"])
    return d


def click_account_card(page, greeting_name):
    """Klik tombol "Masuk Dashboard" pada kartu akun `greeting_name`.

    Implementasi final: setiap kartu adalah kontainer st-key-landing_acct_i
    berisi nama akun (.card-title) + satu st.button "Masuk Dashboard"
    (on_click=core.enter_account). Strategi utama mencocokkan kontainer
    kartu lewat teks namanya lalu mengklik tombol di dalamnya; fallback
    generik (leluhur bisa-klik dari elemen nama) dipertahankan untuk
    perubahan desain kecil. Mengembalikan (ok, label, error).
    """
    labels_to_try = BASELINE[greeting_name]["card_labels"]
    for lab in labels_to_try:
        try:
            clicked = page.evaluate("""(label) => {
              const cards = Array.from(
                document.querySelectorAll('[class*="st-key-landing_acct"]'));
              for (const card of cards) {
                if ((card.textContent || '').includes(label)) {
                  const btn = card.querySelector('button');
                  if (btn) { btn.click(); return 'card-button'; }
                }
              }
              const els = Array.from(document.querySelectorAll('body *'));
              const hit = els.find(e => {
                let t = '';
                for (const n of e.childNodes) if (n.nodeType === 3) t += n.textContent;
                return t.trim() === label;
              }) || els.find(e => (e.textContent || '').trim() === label);
              if (!hit) return false;
              let cur = hit;
              for (let i = 0; i < 6 && cur; i++) {
                const cs = getComputedStyle(cur);
                if (cur.tagName === 'BUTTON' || cur.tagName === 'A'
                    || cur.getAttribute('role') === 'button'
                    || cs.cursor === 'pointer') { cur.click(); return 'ancestor'; }
                cur = cur.parentElement;
              }
              hit.click(); return 'self';
            }""", lab)
            if clicked:
                return True, f"{lab} [{clicked}]", None
        except Exception as ex:
            return False, lab, f"{type(ex).__name__}: {ex}"
        try:
            loc = page.get_by_text(lab, exact=False).first
            if loc.count() > 0:
                loc.click(timeout=5000)
                return True, lab, None
        except Exception:
            pass
    return False, None, "tidak ada kartu akun / tombol masuk yang bisa diklik"


def goto_module(page, display_label, marker, timeout=90000):
    """Pindah modul lewat pill navigasi. Lokator utama mengikuti pola
    bukti lama ([data-testid=stButtonGroup] button); fallback tombol
    by-role seperti journey Tahap 2/6 bila testid berbeda."""
    btn = page.locator('[data-testid="stButtonGroup"] button',
                       has_text=display_label)
    try:
        btn.first.click(timeout=15000)
    except Exception:
        page.get_by_role("button", name=display_label).first.click(timeout=30000)
    page.get_by_text(marker, exact=False).first.wait_for(timeout=timeout)
    page.wait_for_timeout(2000)


def wait_initial(page, timeout=120000):
    """Tunggu render awal selesai: kartu landing ATAU sapaan/KPI dashboard.
    Muat model +/-18-30 dtk; loading bermerek tampil lebih dulu."""
    try:
        page.wait_for_function(
            """() => {
              const t = document.body.innerText || '';
              return !!document.querySelector('[class*="st-key-landing_acct"]')
                || !!document.querySelector('.kpi-value')
                || t.includes('Pilih restoran untuk masuk ke dashboard')
                || (t.includes('Halo,') && t.length > 400);
            }""", timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(3000)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return path

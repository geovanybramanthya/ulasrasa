"""Probe AppTest: laporkan caption engine + teks kunci yang ter-render di app.

Usage: py probe_apptest.py [timeout]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from streamlit.testing.v1 import AppTest

timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 600
at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=timeout)
at.run(timeout=timeout)
print(f"exceptions={len(at.exception)} errors={len(at.error)}")
caps = []
for c in at.caption:
    v = getattr(c, "value", None) or getattr(c, "body", "")
    caps.append(str(v))
for c in caps:
    if "Engine ABSA" in c or "Mode rekomendasi" in c:
        print("CAPTION:", c)
titles = [str(getattr(t, "value", "")) for t in at.title]
print("TITLES:", titles[:2])
md_text = " ".join(str(getattr(m, "value", "")) for m in at.markdown)
for needle in ["Kitchen Health Score", "Ringkasan Kesehatan Dapur"]:
    print(f"MARKDOWN contains '{needle}':", needle in md_text)
sys.exit(0 if len(at.exception) == 0 else 1)

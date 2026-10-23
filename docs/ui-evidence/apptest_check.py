"""AppTest check: jalankan app.py via Streamlit AppTest, laporkan exception.

Usage: py apptest_check.py [timeout_detik]
Exit 0 bila 0 exception dan 0 error element.
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
n_exc = len(at.exception)
n_err = len(at.error)
print(f"APPTEST exceptions={n_exc} errors={n_err}")
for e in at.exception:
    print("EXCEPTION:", e.value if hasattr(e, "value") else e)
for e in at.error:
    print("ERROR ELEMENT:", e.value if hasattr(e, "value") else e)
# konteks sesi dasar untuk bukti
try:
    print("SESSION active_module_name =", at.session_state.get("active_module_name"))
except Exception as ex:
    print("SESSION read fail:", ex)
sys.exit(0 if (n_exc == 0 and n_err == 0) else 1)

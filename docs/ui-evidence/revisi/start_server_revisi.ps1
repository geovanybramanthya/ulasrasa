# start_server_revisi.ps1 - salinan pola docs/ui-evidence/start_server.ps1
# untuk harness revisi: server Streamlit detached di port bebas (default 8525).
# Pemakaian: powershell -File docs/ui-evidence/revisi/start_server_revisi.ps1 [-Port 8525]
# Catatan: harness .py di folder ini bisa menyalakan servernya sendiri;
# skrip ini untuk koordinator yang mau menjalankan server manual.
param([int]$Port = 8525)
$repo = 'C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa'
$py = 'C:\Users\geova\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$cmd = '"' + $py + '" -m streamlit run app.py --server.port ' + $Port + ' --server.headless true --browser.gatherUsageStats false'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $repo }
"ReturnValue=$($r.ReturnValue) ProcessId=$($r.ProcessId) Port=$Port"

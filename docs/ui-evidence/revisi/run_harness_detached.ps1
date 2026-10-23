# run_harness_detached.ps1 - jalankan harness revisi secara detached
# (bertahan sesudah sesi SSH putus) dengan stdout+stderr ke file log.
# Pola Win32_Process Create sama seperti start_server.ps1 di repo ini.
# Pemakaian:
#   powershell -File run_harness_detached.ps1 -Script font_sweep_open_states.py -Log font_sweep_open_states_awal.log -ArgsLine "--tag awal"
param(
  [Parameter(Mandatory=$true)][string]$Script,
  [Parameter(Mandatory=$true)][string]$Log,
  [string]$ArgsLine = ""
)
$repo = 'C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa'
$here = Join-Path $repo 'docs\ui-evidence\revisi'
$py = 'C:\Users\geova\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$logPath = Join-Path $here $Log
$inner = 'cd /d "' + $repo + '" && "' + $py + '" docs\ui-evidence\revisi\' + $Script + ' ' + $ArgsLine + ' > "' + $logPath + '" 2>&1'
$cmd = 'cmd.exe /c "' + $inner + '"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $repo }
"LAUNCHED Script=$Script PID=$($r.ProcessId) ReturnValue=$($r.ReturnValue) Log=$logPath"

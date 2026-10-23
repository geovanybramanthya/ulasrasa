$repo = 'C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa'
$py = 'C:\Users\geova\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$log = Join-Path $repo 'docs\ui-evidence\audit-fix3\capture_rincian2.log'
$args = 'docs\ui-evidence\capture.py --url http://localhost:8517 --out audit-fix3/rincian-1440.png --width 1440 --height 900 --wait-text "Halo," --click-text "Rincian Aspek" --full-page --settle-ms 9000'
$cmd = 'cmd /c ""' + $py + '" ' + $args + ' > "' + $log + '" 2>&1"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $repo }
"ReturnValue=$($r.ReturnValue) ProcessId=$($r.ProcessId) Log=$log"

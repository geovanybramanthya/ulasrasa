param([string]$Tag = "before")
$repo = 'C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa'
$py = 'C:\Users\geova\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$log = Join-Path $repo ('docs\ui-evidence\audit-fix3\sweep_svg_' + $Tag + '.log')
$cmd = 'cmd /c ""' + $py + '" docs\ui-evidence\audit-fix3\font_sweep_svg.py --url http://localhost:8517 --tag ' + $Tag + ' > "' + $log + '" 2>&1"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $repo }
"ReturnValue=$($r.ReturnValue) ProcessId=$($r.ProcessId) Log=$log"

param([string]$Script, [string]$LogName, [string]$ExtraArgs = "")
$repo = 'C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa'
$py = 'C:\Users\geova\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$log = Join-Path $repo ('docs\ui-evidence\audit-fix2\' + $LogName)
$cmd = 'cmd /c ""' + $py + '" ' + $Script + ' ' + $ExtraArgs + ' > "' + $log + '" 2>&1"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $repo }
"ReturnValue=$($r.ReturnValue) ProcessId=$($r.ProcessId) Log=$log"

$ErrorActionPreference = "Continue"
Set-Location "C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa"
New-Item -ItemType Directory -Force training | Out-Null
Write-Output "=== creating venv with py -3.11 ==="
py -3.11 -m venv training\venv
if (-not (Test-Path training\venv\Scripts\python.exe)) { Write-Output "VENV_FAILED"; exit 1 }
$py = "training\venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
Write-Output "=== installing torch 2.5.1 cu124 ==="
& $py -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124
Write-Output "=== installing transformers etc ==="
& $py -m pip install transformers scikit-learn pandas numpy accelerate
Write-Output "=== verify cuda ==="
& $py -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('device', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); import transformers, sklearn, pandas, numpy; print('transformers', transformers.__version__); print('sklearn', sklearn.__version__)"
Write-Output "=== SETUP_DONE ==="

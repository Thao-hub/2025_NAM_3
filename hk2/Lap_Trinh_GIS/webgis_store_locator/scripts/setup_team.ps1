param(
    [switch]$NoVenv,
    [switch]$RecreateVenv,
    [switch]$FlushData,
    [switch]$RunServer,
    [int]$Port = 8000,
    [string]$FixturePath = "modules/store/fixtures/store_data.json"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Step {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Action
    )
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Action
    if ((Test-Path Variable:LASTEXITCODE) -and $LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or not in PATH."
}

$venvDir = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts/python.exe"
$venvActivate = Join-Path $venvDir "Scripts/Activate.ps1"

if (-not $NoVenv) {
    if ($RecreateVenv -and (Test-Path $venvDir)) {
        Write-Host "Removing old .venv" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvDir
    }

    if (-not (Test-Path $venvPython)) {
        Invoke-Step -Name "Create virtual environment" -Action { python -m venv .venv }
    }

    if (-not (Test-Path $venvActivate)) {
        throw "Cannot find .venv activation script."
    }

    . $venvActivate
    if (-not $env:VIRTUAL_ENV) {
        throw "Cannot activate virtual environment."
    }
}

Invoke-Step -Name "Install dependencies" -Action { python -m pip install --upgrade pip }
Invoke-Step -Name "Install requirements" -Action { python -m pip install -r requirements.txt }
Invoke-Step -Name "Run migrations" -Action { python manage.py migrate }

if ($FlushData) {
    Invoke-Step -Name "Flush existing data" -Action { python manage.py flush --noinput }
    Invoke-Step -Name "Run migrations after flush" -Action { python manage.py migrate }
}

if (Test-Path $FixturePath) {
    Invoke-Step -Name "Load fixture data" -Action { python manage.py loaddata $FixturePath }
} else {
    Write-Host "Fixture not found: $FixturePath" -ForegroundColor Yellow
}

Invoke-Step -Name "Django system check" -Action { python manage.py check }

Write-Host "" 
Write-Host "Setup completed." -ForegroundColor Green
Write-Host "Next: python manage.py runserver" -ForegroundColor Green

if ($RunServer) {
    Invoke-Step -Name "Run development server" -Action { python manage.py runserver 127.0.0.1:$Port }
}

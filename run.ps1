# run.ps1 - Test Isolated App entry script
Write-Host "========================================="
Write-Host "Starting TestIsolatedApp Backend Script..."
Write-Host "========================================="

# Resolve local virtual environment python interpreter path
$PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

# Verify that python can import the uv-installed requests package
Write-Host "Verifying Python dependencies inside the virtual environment using: $PythonExe"
& $PythonExe -c "import requests; print('requests version successfully imported:', requests.__version__)"

# Start python backend server
Write-Host "Launching server/app.py..."
& $PythonExe server/app.py

# run.ps1 - Test Isolated App entry script
Write-Host "========================================="
Write-Host "Starting TestIsolatedApp Backend Script..."
Write-Host "========================================="

# Verify that python can import the uv-installed requests package
Write-Host "Verifying Python dependencies inside the virtual environment..."
python -c "import requests; print('requests version successfully imported:', requests.__version__)"

# Start python backend server
Write-Host "Launching server/app.py..."
python server/app.py

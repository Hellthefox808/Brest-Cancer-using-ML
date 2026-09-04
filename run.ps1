Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting Breast Cancer Detection Web Application" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

$anacondaPython = "C:\Users\ravir\anaconda3\python.exe"
if (Test-Path $anacondaPython) {
    Write-Host "Using Python: $anacondaPython" -ForegroundColor Gray
    & $anacondaPython app.py
} else {
    Write-Host "Using default system python" -ForegroundColor Gray
    python app.py
}

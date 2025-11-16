Write-Host "Searching for __pycache__ folders..." -ForegroundColor Yellow

$pycacheFolders = Get-ChildItem -Path . -Name "__pycache__" -Recurse -Directory -Force

if ($pycacheFolders.Count -eq 0) {
    Write-Host "No __pycache__ folders found." -ForegroundColor Green
    exit 0
}

Write-Host "Found $($pycacheFolders.Count) __pycache__ folders:" -ForegroundColor Cyan
foreach ($folder in $pycacheFolders) {
    Write-Host "  $folder" -ForegroundColor White
}

foreach ($folder in $pycacheFolders) {
    try {
        Remove-Item -Path $folder -Recurse -Force
    }
    catch {
        Write-Host "Failed: $folder - $($_.Exception.Message)" -ForegroundColor Red
    }
}
cls
Write-Host "Done!" -ForegroundColor Green

# DeepSeek-V3.2-Exp Generator

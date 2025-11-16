$startTime = Get-Date
Write-Host "Running __pycache__ cleanup..." -ForegroundColor Yellow
.\tools\delete_pycache.ps1

$targetPath = ".\..\hoj-tool - backup"

if (Test-Path $targetPath) {
    Get-ChildItem -Path $targetPath -Force | 
    Where-Object { $_.Name -ne ".venv" } | 
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "Deleted." -ForegroundColor Green
} else {
    Write-Host "Target path does not exist." -ForegroundColor Red
    exit 1
}

Get-ChildItem -Path "." | Where-Object { $_.Name -ne ".venv" -and $_.Name -ne "backup.ps1" } | Copy-Item -Destination ".\..\hoj-tool - backup" -Recurse -Force

cls
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMilliseconds
Write-Host "Done ! ($([math]::Round($duration))ms)" -ForegroundColor Green

# DeepSeek-V3.2-Exp Generator

$startTime = Get-Date
Write-Host "Starting backup restore..." -ForegroundColor Yellow

$backupPath = ".\..\hoj-tool - backup"

# Check if backup directory exists
if (-not (Test-Path $backupPath)) {
    Write-Host "Backup directory does not exist: $backupPath" -ForegroundColor Red
    exit 1
}

Write-Host "Cleaning current directory (excluding .venv)..." -ForegroundColor Yellow

# Clean current directory excluding .venv
Get-ChildItem -Path "." -Force | 
Where-Object { $_.Name -ne ".venv" -and $_.Name -ne "restore_backup.ps1" } | 
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Restoring files from backup..." -ForegroundColor Yellow

# Copy files from backup excluding .venv
Get-ChildItem -Path $backupPath | 
Where-Object { $_.Name -ne ".venv" } | 
Copy-Item -Destination "." -Recurse -Force

cls
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMilliseconds
Write-Host "Backup restored successfully! ($([math]::Round($duration))ms)" -ForegroundColor Green

# DeepSeek-V3.2-Exp Generator

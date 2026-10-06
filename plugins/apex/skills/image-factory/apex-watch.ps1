# apex-watch.ps1  -  APEX v2 watcher: Google Drive hand-off -> live page with images, by itself
# ONE-TIME SETUP (then never again):   .\apex-watch.ps1 -Install
#   The watcher then starts by itself every time you sign in to Windows (minimized window in the
#   taskbar), and starts right now too. Nothing to type for new products, changes or retries.
# Other commands (all optional):
#   .\apex-watch.ps1                 start watching in this window
#   .\apex-watch.ps1 -Once           check once and stop
#   .\apex-watch.ps1 -Retry <slug>   run a product again (or put RETRY.txt into APEX\<slug>\ in Drive)
#   .\apex-watch.ps1 -Uninstall      stop starting with Windows
# The output of every stage: the watcher window, apex-logs\<slug>.log, and in Google Drive
# APEX\<slug>\STATUS.txt + apex-log.txt.

param(
    [switch]$Once,
    [string]$Retry,
    [switch]$Install,
    [switch]$Uninstall
)

$factory = if ($env:IMAGE_FACTORY_DIR) { $env:IMAGE_FACTORY_DIR } else { $PSScriptRoot }
Set-Location $factory
$startup  = [Environment]::GetFolderPath('Startup')
$shortcut = Join-Path $startup 'APEX watcher.lnk'

if ($Uninstall) {
    if (Test-Path $shortcut) { Remove-Item $shortcut -Force }
    Write-Host "APEX watcher no longer starts with Windows. (A window that is open now keeps running until you close it.)" -ForegroundColor Yellow
    exit 0
}

if ($Install) {
    $script = Join-Path $factory 'apex-watch.ps1'
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($shortcut)
    $lnk.TargetPath = (Get-Command powershell.exe).Source
    $lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
    $lnk.WorkingDirectory = $factory
    $lnk.WindowStyle = 7          # minimized
    $lnk.Description = 'APEX watcher: Google Drive -> live product page'
    $lnk.Save()
    Write-Host "Done: the APEX watcher now starts by itself when you sign in to Windows." -ForegroundColor Green
    Write-Host "Starting it now (minimized window 'APEX watcher' in the taskbar)..." -ForegroundColor Green
    Start-Process -FilePath $shortcut
    exit 0
}

$host.UI.RawUI.WindowTitle = 'APEX watcher'
$pyArgs = @("apex_watch.py")
if ($Once)  { $pyArgs += "--once" }
if ($Retry) { $pyArgs += @("--retry", $Retry) }
py @pyArgs
exit $LASTEXITCODE

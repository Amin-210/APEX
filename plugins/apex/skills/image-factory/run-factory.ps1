# run-factory.ps1  -  APEX step 4 of 4, Image Factory: images generated and uploaded
# Save this file in your image-factory folder, then run for any product:
#   .\run-factory.ps1 swift-chopper              (generate, then upload directly)
#   .\run-factory.ps1 swift-chopper -NoUpload    (generate only)
# Optional: -Photos C:\path\to\photos  (default: Desktop\<slug>-photos or Desktop\<first word>-photos)

param(
    [Parameter(Mandatory = $true)][string]$Slug,
    [string]$Photos,
    [switch]$NoUpload
)

$ErrorActionPreference = 'Stop'
$factory = if ($env:IMAGE_FACTORY_DIR) { $env:IMAGE_FACTORY_DIR } else { $PSScriptRoot }
$home_   = $env:USERPROFILE
$search  = @("$home_\Downloads", "$home_\Desktop", "$home_\Documents")

Set-Location $factory
Write-Host "`n=== APEX | step 4/4 | Image Factory | $Slug ===" -ForegroundColor Magenta

# Store logins live ONLY in .env.<store>. Active SHOPIFY_ lines in .env (e.g. copied from
# .env.example) override them and cause "401 Invalid API key". Switch them off, with a backup.
function Fix-EnvOverride {
    $envFile = Join-Path $factory '.env'
    if (-not (Test-Path $envFile)) { return }
    $storeFiles = Get-ChildItem $factory -Force -File -Filter '.env.*' |
        Where-Object { $_.Name -notin @('.env.example', '.env.bak') }
    if (-not $storeFiles) { return }
    $lines = @(Get-Content $envFile)
    if (-not ($lines | Where-Object { $_ -match '^\s*SHOPIFY_' })) { return }
    Copy-Item $envFile "$envFile.bak" -Force
    $fixed = $lines | ForEach-Object { if ($_ -match '^\s*SHOPIFY_') { '# ' + $_.TrimStart() } else { $_ } }
    [System.IO.File]::WriteAllLines($envFile, [string[]]$fixed)   # UTF-8 without BOM
    Write-Host "Fixed: switched off the SHOPIFY_ lines in .env (the login lives in .env.<store>). Backup: .env.bak" -ForegroundColor Yellow
}
Fix-EnvOverride

# Generate, then (unless -NoUpload) upload right away
function Finish-Run {
    if ($LASTEXITCODE -ne 0) { Write-Host "Stopped: fix the message above and run the same command again." -ForegroundColor Red; exit $LASTEXITCODE }
    if ($NoUpload) { exit 0 }
    Write-Host "`n=== Uploading to Shopify ===" -ForegroundColor Cyan
    py factory.py $Slug --yes
    exit $LASTEXITCODE
}

# Product already set up earlier -> just continue generating
if (Test-Path "$factory\products\$Slug") {
    Write-Host "Product '$Slug' already set up, continuing..." -ForegroundColor Cyan
    Write-Host "`n=== Generating (only what is missing) ===" -ForegroundColor Cyan
    py factory.py $Slug --no-upload
    Finish-Run
}

function Find-Newest($pattern) {
    Get-ChildItem $search -Filter $pattern -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

# 1. Find the page-engine files (also catches "name (1).json" from repeat downloads)
$json = Find-Newest "$Slug-images*.json"
$md   = Find-Newest "$Slug-image-prompts*.md"
if (-not $json) {
    Write-Host "Not found: $Slug-images.json in Downloads, Desktop or Documents." -ForegroundColor Red
    Write-Host "Download it (and $Slug-image-prompts.md) from the chat first, then run this again." -ForegroundColor Yellow
    exit 1
}

# 2. Copy them with clean names into incoming\<slug>\
$inbox = "$factory\incoming\$Slug"
New-Item -ItemType Directory -Force -Path $inbox | Out-Null
Copy-Item $json.FullName "$inbox\$Slug-images.json" -Force
if ($md) { Copy-Item $md.FullName "$inbox\$Slug-image-prompts.md" -Force }
Write-Host "Using $($json.FullName)" -ForegroundColor Green

# 3. Find the photos folder
if (-not $Photos) {
    $first = $Slug.Split('-')[0]
    foreach ($c in @("$home_\Desktop\$Slug-photos", "$home_\Desktop\$first-photos")) {
        if (Test-Path $c) { $Photos = $c; break }
    }
}
if (-not $Photos -or -not (Test-Path $Photos)) {
    Write-Host "No photos folder found. Make Desktop\$Slug-photos with 1-3 product photos, or pass -Photos <folder>." -ForegroundColor Red
    exit 1
}
Write-Host "Photos: $Photos" -ForegroundColor Green

# 4. Generate, then upload
Write-Host "`n=== Generating ===" -ForegroundColor Cyan
py factory.py "$inbox\$Slug-images.json" --photos $Photos --no-upload
Finish-Run

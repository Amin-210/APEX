# new-product.ps1  -  APEX step 2 of 4, Product setup: create the product and its unique template
# Flow:  PageEngine  ->  .\new-product.ps1 <slug>  ->  Claude Code in VS Code designs the page
#        in that template (prompt is on your clipboard)  ->  .\run-factory.ps1 <slug>
#
#   .\new-product.ps1 <slug>           product + unique template (assigned), prompt for Claude Code
#   .\new-product.ps1 <slug> -DryRun   only check that everything is ready, change nothing
#   .\new-product.ps1 <slug> -NoVSCode do not open VS Code at the end
#   .\new-product.ps1 <slug> -ProductOnly  only update the product (price, compare-at, tax,
#                                        inventory, shipping), no template, no Claude Code prompt
# It takes the newest PageEngine files from Downloads, Desktop or Documents.

param(
    [Parameter(Mandatory = $true)][string]$Slug,
    [switch]$DryRun,
    [switch]$NoVSCode,
    [switch]$ProductOnly
)

$ErrorActionPreference = 'Stop'
$factory = if ($env:IMAGE_FACTORY_DIR) { $env:IMAGE_FACTORY_DIR } else { $PSScriptRoot }
$home_   = $env:USERPROFILE
$search  = @("$home_\Downloads", "$home_\Desktop", "$home_\Documents")
Set-Location $factory

function Find-Newest($pattern) {
    Get-ChildItem $search -Filter $pattern -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

Write-Host "`n=== APEX | step 2/4 | Product setup | $Slug ===" -ForegroundColor Magenta
Write-Host "`n=== Collecting the PageEngine files for '$Slug' ===" -ForegroundColor Cyan
$inbox = "$factory\incoming\$Slug"
New-Item -ItemType Directory -Force -Path $inbox | Out-Null

$wanted = @(
    @{ Pattern = "$Slug-product*.json";               Name = "$Slug-product.json";               Required = $true  },
    @{ Pattern = "product-description-$Slug*.liquid"; Name = "product-description-$Slug.liquid"; Required = $true  },
    @{ Pattern = "journey-badge*.liquid";             Name = "journey-badge.liquid";             Required = $false },
    @{ Pattern = "$Slug-images*.json";                Name = "$Slug-images.json";                Required = $false },
    @{ Pattern = "$Slug-image-prompts*.md";           Name = "$Slug-image-prompts.md";           Required = $false }
)
foreach ($w in $wanted) {
    $f = Find-Newest $w.Pattern
    if ($f) {
        Copy-Item $f.FullName "$inbox\$($w.Name)" -Force
        Write-Host "  found   $($f.FullName)" -ForegroundColor Green
    } elseif ($w.Required) {
        Write-Host "  missing $($w.Name): download it from the chat into Downloads, then run this again." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "  (not found: $($w.Name))" -ForegroundColor DarkGray
    }
}

$pyArgs = @("product_setup.py", "$inbox\$Slug-product.json")
if ($DryRun) { $pyArgs += "--dry-run" }
if ($ProductOnly) { $pyArgs += "--product-only" }
py @pyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($DryRun -or $ProductOnly) { exit 0 }

# Hand-off to Claude Code: prompt on the clipboard, VS Code opened on the theme folder
$prompt = "$inbox\claude-code-prompt.md"
if (Test-Path $prompt) {
    Get-Content $prompt -Raw | Set-Clipboard
    Write-Host "`n=== Claude Code prompt copied to your clipboard ===" -ForegroundColor Cyan
    Write-Host "  (also saved in $prompt)"
}
$theme = if ($env:THEME_DIR) { $env:THEME_DIR } else { $null }
if (-not $NoVSCode -and $theme -and (Get-Command code -ErrorAction SilentlyContinue)) {
    code $theme
    Write-Host "  VS Code opened on ${theme}: open Claude Code and paste (Ctrl+V)." -ForegroundColor Green
}
Write-Host "`nAPEX next: step 3/4 Claude Code design (paste the prompt), then step 4/4:  .\run-factory.ps1 $Slug" -ForegroundColor Yellow

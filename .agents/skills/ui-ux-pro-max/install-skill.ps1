#!/usr/bin/env pwsh
# install-skill.ps1 - Downloads UI UX Pro Max skill from GitHub
# Run: powershell -ExecutionPolicy Bypass -File .agents/skills/ui-ux-pro-max/install-skill.ps1

$ErrorActionPreference = "Stop"
$baseUrl = "https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main"
$skillDir = Join-Path $PSScriptRoot ""

# Create directories
$dirs = @(
    "scripts",
    "data",
    "data/stacks"
)
foreach ($d in $dirs) {
    $path = Join-Path $skillDir $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# Files to download (source path -> local path)
$files = @(
    @("src/ui-ux-pro-max/scripts/search.py", "scripts/search.py"),
    @("src/ui-ux-pro-max/scripts/core.py", "scripts/core.py"),
    @("src/ui-ux-pro-max/scripts/design_system.py", "scripts/design_system.py"),
    @("src/ui-ux-pro-max/data/products.csv", "data/products.csv"),
    @("src/ui-ux-pro-max/data/styles.csv", "data/styles.csv"),
    @("src/ui-ux-pro-max/data/colors.csv", "data/colors.csv"),
    @("src/ui-ux-pro-max/data/typography.csv", "data/typography.csv"),
    @("src/ui-ux-pro-max/data/landing.csv", "data/landing.csv"),
    @("src/ui-ux-pro-max/data/charts.csv", "data/charts.csv"),
    @("src/ui-ux-pro-max/data/ux-guidelines.csv", "data/ux-guidelines.csv"),
    @("src/ui-ux-pro-max/data/motion.csv", "data/motion.csv"),
    @("src/ui-ux-pro-max/data/icons.csv", "data/icons.csv"),
    @("src/ui-ux-pro-max/data/design.csv", "data/design.csv"),
    @("src/ui-ux-pro-max/data/ui-reasoning.csv", "data/ui-reasoning.csv"),
    @("src/ui-ux-pro-max/data/google-fonts.csv", "data/google-fonts.csv"),
    @("src/ui-ux-pro-max/data/react-performance.csv", "data/react-performance.csv"),
    @("src/ui-ux-pro-max/data/app-interface.csv", "data/app-interface.csv"),
    @("src/ui-ux-pro-max/data/draft.csv", "data/draft.csv")
)

Write-Host "=== UI/UX Pro Max Skill Installer ===" -ForegroundColor Cyan
Write-Host "Downloading $($files.Count) files from GitHub..." -ForegroundColor Yellow

$success = 0
$failed = 0

foreach ($file in $files) {
    $url = "$baseUrl/$($file[0])"
    $dest = Join-Path $skillDir $file[1]
    
    try {
        Write-Host "  Downloading $($file[1])..." -NoNewline
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        Write-Host " OK" -ForegroundColor Green
        $success++
    } catch {
        Write-Host " FAILED: $_" -ForegroundColor Red
        $failed++
    }
}

# Also download stack-specific files
$stacks = @(
    "html-tailwind", "react", "nextjs", "astro", "vue", "nuxtjs", "nuxt-ui",
    "svelte", "swiftui", "react-native", "flutter", "shadcn", "jetpack-compose",
    "threejs", "angular", "laravel", "javafx", "wpf", "winui", "avalonia", "uno", "uwp"
)

Write-Host "`nDownloading stack-specific guides..." -ForegroundColor Yellow
foreach ($stack in $stacks) {
    $url = "$baseUrl/src/ui-ux-pro-max/data/stacks/$stack.csv"
    $dest = Join-Path $skillDir "data/stacks/$stack.csv"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -ErrorAction SilentlyContinue
        $success++
    } catch {
        # Stack files may not all exist, skip silently
    }
}

Write-Host "`n=== Installation Complete ===" -ForegroundColor Cyan
Write-Host "  Files downloaded: $success" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "  Files failed: $failed" -ForegroundColor Red
}

# Verify Python is available
Write-Host "`nVerifying Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Python not found! Install Python 3.8+ to use this skill." -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
}

# Quick test
Write-Host "`nRunning quick test..." -ForegroundColor Yellow
try {
    $testResult = & python (Join-Path $skillDir "scripts/search.py") "modern dashboard" --domain style -n 1 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Search test: PASSED" -ForegroundColor Green
        Write-Host $testResult
    } else {
        Write-Host "  Search test: FAILED (exit code $LASTEXITCODE)" -ForegroundColor Red
        Write-Host $testResult
    }
} catch {
    Write-Host "  Search test: SKIPPED (Python not available)" -ForegroundColor Yellow
}

Write-Host "`nDone! The skill is installed at: $skillDir" -ForegroundColor Cyan

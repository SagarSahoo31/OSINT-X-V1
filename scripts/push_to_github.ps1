<#
.SYNOPSIS
    Automated Git & GitHub Sync Pipeline for OSINT-X.
.DESCRIPTION
    Initializes git repository, sets up main branch, stages files, generates semantic commit,
    and pushes to GitHub remote.
.PARAMETER RemoteUrl
    Optional GitHub repository URL (e.g. https://github.com/username/osint-x.git).
.PARAMETER CommitMessage
    Optional custom commit message.
#>

param(
    [string]$RemoteUrl = "",
    [string]$CommitMessage = "feat: OSINT-X defensive cybersecurity intelligence platform (Phases 1-20 release)"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OSINT-X — Automated GitHub DevOps Deployment Pipeline   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Git Installation
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Initialize Git if needed
if (-not (Test-Path ".git")) {
    Write-Host "[1/5] Initializing Git repository with 'main' branch..." -ForegroundColor Yellow
    git init -b main
} else {
    Write-Host "[1/5] Git repository already initialized." -ForegroundColor Green
    git branch -M main
}

# 3. Stage All Changes
Write-Host "[2/5] Staging files (respecting .gitignore)..." -ForegroundColor Yellow
git add .

# 4. Check Status & Commit
$status = git status --porcelain
if ($status) {
    Write-Host "[3/5] Committing changes with Conventional Commit message..." -ForegroundColor Yellow
    git commit -m "$CommitMessage"
} else {
    Write-Host "[3/5] No new changes to commit." -ForegroundColor Green
}

# 5. Configure Remote
$existingRemote = git remote get-url origin 2>$null
if (-not $existingRemote) {
    if (-not $RemoteUrl) {
        Write-Host ""
        Write-Host "No GitHub remote URL configured." -ForegroundColor Yellow
        $RemoteUrl = Read-Host "Enter your GitHub Repository URL (e.g., https://github.com/YOUR_USER/osint-x.git)"
    }
    
    if ($RemoteUrl) {
        Write-Host "[4/5] Adding remote origin: $RemoteUrl" -ForegroundColor Yellow
        git remote add origin $RemoteUrl
    } else {
        Write-Host "[WARNING] No remote URL provided. Commit created locally." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "[4/5] Remote origin is configured: $existingRemote" -ForegroundColor Green
}

# 6. Push to GitHub
Write-Host "[5/5] Pushing to GitHub (main branch)..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed OSINT-X to GitHub!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Push completed with status code $LASTEXITCODE. If this is a newly created repo with files, you may need to force push: git push -u origin main --force" -ForegroundColor Yellow
}

#!/usr/bin/env bash
set -e

REMOTE_URL=${1:-""}
COMMIT_MSG=${2:-"feat: OSINT-X defensive cybersecurity intelligence platform (Phases 1-20 release)"}

echo "=========================================================="
echo "  OSINT-X — Automated GitHub DevOps Deployment Pipeline   "
echo "=========================================================="

if [ ! -d ".git" ]; then
    echo "[1/5] Initializing Git repository on 'main' branch..."
    git init -b main
else
    echo "[1/5] Git repository already initialized."
    git branch -M main
fi

echo "[2/5] Staging files..."
git add .

if ! git diff --cached --quiet; then
    echo "[3/5] Committing changes..."
    git commit -m "$COMMIT_MSG"
else
    echo "[3/5] Nothing to commit."
fi

if ! git remote | grep -q "origin"; then
    if [ -z "$REMOTE_URL" ]; then
        read -p "Enter your GitHub Repository URL (e.g. https://github.com/user/osint-x.git): " REMOTE_URL
    fi
    if [ -n "$REMOTE_URL" ]; then
        echo "[4/5] Setting remote origin..."
        git remote add origin "$REMOTE_URL"
    fi
else
    echo "[4/5] Remote origin configured: $(git remote get-url origin)"
fi

echo "[5/5] Pushing to GitHub..."
git push -u origin main

echo "✅ Done!"

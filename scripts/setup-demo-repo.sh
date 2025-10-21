#!/usr/bin/env bash
set -euo pipefail

ROOT_NAME=${1:-demo-forked}
ROOT_DIR=$(pwd)
UPSTREAM_BARE="$ROOT_DIR/${ROOT_NAME}-upstream.git"
UPSTREAM_WORKDIR=$(mktemp -d)
FORK_DIR="$ROOT_DIR/${ROOT_NAME}"
ORIGIN_BARE="$ROOT_DIR/${ROOT_NAME}-origin.git"

if [[ -d "$FORK_DIR" ]]; then
  echo "❌ Directory $FORK_DIR already exists. Remove it or pass a different name." >&2
  exit 1
fi

if [[ -d "$UPSTREAM_BARE" ]]; then
  echo "❌ Upstream repo $UPSTREAM_BARE already exists. Remove it or pass a different name." >&2
  exit 1
fi

if [[ -d "$ORIGIN_BARE" ]]; then
  echo "❌ Origin repo $ORIGIN_BARE already exists. Remove it or pass a different name." >&2
  exit 1
fi

# Create upstream bare repository
git init --bare "$UPSTREAM_BARE" >/dev/null

# Seed upstream with initial content
git clone "$UPSTREAM_BARE" "$UPSTREAM_WORKDIR/upstream-src" >/dev/null
pushd "$UPSTREAM_WORKDIR/upstream-src" >/dev/null
  git config user.email "demo@example.com"
  git config user.name "Forked Demo"

  mkdir -p api/contracts src
  cat <<'YAML' > api/contracts/v1.yaml
openapi: 3.0.0
info:
  title: Demo Contract
  version: 1.0.0
paths: {}
YAML

  cat <<'PY' > src/service.py
print("hello upstream")
PY

  cat <<'MD' > README.md
# Demo Upstream Repository

Base repository used to demonstrate Forked CLI workflows.
MD

  git add .
  git commit -m "feat: seed upstream" >/dev/null
  git push origin main >/dev/null

  # create patch branch seeds
  git checkout -b patch/contract-update >/dev/null
  cat <<'YAML' > api/contracts/v1.yaml
openapi: 3.0.0
info:
  title: Demo Contract
  version: 1.1.0
paths:
  /health:
    get:
      summary: Health check
YAML
  git commit -am "feat: update contract" >/dev/null
  git push origin patch/contract-update >/dev/null

  git checkout main >/dev/null
  git checkout -b patch/service-logging >/dev/null
  cat <<'PY' > src/service.py
import logging

logging.basicConfig(level=logging.INFO)

print("hello upstream with logging")
PY
  git commit -am "feat: add service logging" >/dev/null
  git push origin patch/service-logging >/dev/null
  git checkout main >/dev/null
popd >/dev/null

# Create origin bare repo to simulate fork remote (optional but useful)
git clone --bare "$UPSTREAM_WORKDIR/upstream-src" "$ORIGIN_BARE" >/dev/null

# Clone working fork
git clone "$ORIGIN_BARE" "$FORK_DIR" >/dev/null
pushd "$FORK_DIR" >/dev/null
  git config user.email "demo@example.com"
  git config user.name "Forked Demo"

  # Add upstream remote pointing back to upstream bare repo
  git remote add upstream "$UPSTREAM_BARE"
  git fetch upstream >/dev/null

  # Create sentinel directories for fork customization
  mkdir -p config/forked branding
  cat <<'CFG' > config/forked/settings.yaml
worktree:
  enabled: true
CFG
  cat <<'TXT' > branding/banner.txt
Forked Demo Brand Assets
TXT
  git add config/forked branding
  git commit -m "chore: add fork branding" >/dev/null

  # Push to origin for completeness
  git push origin HEAD:main >/dev/null

  # Bring patch branches into fork for local work
  git fetch upstream patch/contract-update:patch/contract-update >/dev/null
  git fetch upstream patch/service-logging:patch/service-logging >/dev/null

  echo "✅ Demo fork ready at $FORK_DIR"
  echo "   Upstream remote: $UPSTREAM_BARE"
  echo "   Origin remote:   $ORIGIN_BARE"
  echo "   Patch branches:  patch/contract-update, patch/service-logging"
  echo "   Sentinel files:  config/forked/**, branding/**"
  echo ""
  echo "Run the smoke checklist from inside $FORK_DIR"
popd >/dev/null

# Cleanup temp worktree
rm -rf "$UPSTREAM_WORKDIR"

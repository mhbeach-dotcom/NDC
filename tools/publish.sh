#!/bin/sh
# Rebuild the page and replace index.html with a password-protected (StatiCrypt) version.
# Usage: NDC_PASSWORD='...' tools/publish.sh
set -e
cd "$(dirname "$0")/.."
: "${NDC_PASSWORD:?set NDC_PASSWORD to the page password}"
python3 tools/build.py
tmp=$(mktemp -d)
npx -y staticrypt index.html -p "$NDC_PASSWORD" --short -d "$tmp" \
  --template-title "Nuclear Deterrence and Coercion — Winter 2026/27" \
  --template-instructions "Enter the password to view this page."
cp "$tmp"/index.html .
rm -rf "$tmp"

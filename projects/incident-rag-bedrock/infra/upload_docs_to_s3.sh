#!/bin/bash
# Upload the incident-ops runbook corpus to the S3 bucket backing the Bedrock KB.
# Usage: BUCKET=reem-amdocs-ai-artifacts-3331 ./infra/upload_docs_to_s3.sh
set -euo pipefail

: "${BUCKET:?Set BUCKET env var, e.g. BUCKET=reem-amdocs-ai-artifacts-3331}"

SRC="${SRC:-./data/sample_documents}"
PREFIX="${PREFIX:-projects/incident-rag-bedrock/data/sample_documents}"

if [[ ! -d "$SRC" ]]; then
  echo "Source directory not found: $SRC" >&2
  echo "Run 'python scripts/build_corpus.py' first to generate the corpus." >&2
  exit 1
fi

DEST="s3://${BUCKET}/${PREFIX}/"
aws s3 sync "$SRC" "$DEST" \
  --exclude ".gitkeep" \
  --exclude "README.md" \
  --exclude "*.tmp"

echo
echo "Uploaded to ${DEST}"
echo "Next: in the Bedrock console, click 'Sync' on the data source"
echo "and wait for status 'Available' before testing the app."

#!/bin/bash
# Upload the incident-ops runbook corpus to the S3 bucket backing the Bedrock KB.
# Usage: BUCKET=my-bucket ./infra/upload_docs_to_s3.sh
set -euo pipefail

: "${BUCKET:?Set BUCKET env var, e.g. BUCKET=incident-rag-kb-rm-2026}"

SRC="${SRC:-../incident-assistant-rag/data/sample_documents}"

if [[ ! -d "$SRC" ]]; then
  echo "Source directory not found: $SRC" >&2
  exit 1
fi

aws s3 sync "$SRC" "s3://${BUCKET}/" \
  --exclude ".gitkeep" \
  --exclude "*.tmp"

echo
echo "Uploaded. Next: in the Bedrock console, click 'Sync' on the data source"
echo "and wait for status 'Available' before testing the app."

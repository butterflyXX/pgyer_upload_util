#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IPA_PATH="文件路径"
PGYER_DESC="版本信息"
UPLOAD_RES=$("$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/pgyer_upload.py" "$IPA_PATH" "$PGYER_DESC")
echo "$UPLOAD_RES"
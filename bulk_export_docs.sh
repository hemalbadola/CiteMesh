#!/usr/bin/env bash
# bulk_export_docs.sh
# Purpose: Bundle documentation and asset folders for delivery or demo distribution.
# Usage: ./bulk_export_docs.sh [-o OUTPUT_ZIP] [-r ROOT]
# Dependencies: bash 4+, zip
# Flags:
#   -o Output zip filename (default: docs_assets_bundle.zip)
#   -r Root directory to scan (default: current working directory)
set -euo pipefail

OUTPUT_FILE="docs_assets_bundle.zip"
ROOT_DIR="$(pwd)"

while getopts ":o:r:" opt; do
  case "$opt" in
    o)
      OUTPUT_FILE="${OPTARG}"
      ;;
    r)
      ROOT_DIR="${OPTARG}"
      ;;
    *)
      echo "Usage: $0 [-o OUTPUT_ZIP] [-r ROOT]" >&2
      exit 1
      ;;
  esac
done

TMP_LIST=$(mktemp)
trap 'rm -f "${TMP_LIST}"' EXIT

find "${ROOT_DIR}" \( -path "*/docs" -o -path "*/assets" \) -type d > "${TMP_LIST}"

if [ ! -s "${TMP_LIST}" ]; then
  echo "No docs or assets directories found under ${ROOT_DIR}" >&2
  exit 1
fi

echo "Creating archive ${OUTPUT_FILE}"
zip -r "${OUTPUT_FILE}" -@ < "${TMP_LIST}"

echo "Archive ready: ${OUTPUT_FILE}"

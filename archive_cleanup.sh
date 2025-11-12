#!/usr/bin/env bash
# archive_cleanup.sh
# Purpose: Clean or archive outdated files within contributor archive folders.
# Usage: ./archive_cleanup.sh [-d DAYS] [-t TARGET_ROOT] [-c]
# Dependencies: bash 4+, find, gzip (optional when using -c)
# Flags:
#   -d Retention window in days (default: 30)
#   -t Target root directory (default: current working directory)
#   -c Compress files older than retention window instead of deleting
set -euo pipefail

RETENTION_DAYS=30
TARGET_ROOT="$(pwd)"
COMPRESS=false

while getopts ":d:t:c" opt; do
  case "$opt" in
    d)
      RETENTION_DAYS="${OPTARG}"
      ;;
    t)
      TARGET_ROOT="${OPTARG}"
      ;;
    c)
      COMPRESS=true
      ;;
    *)
      echo "Usage: $0 [-d DAYS] [-t TARGET_ROOT] [-c]" >&2
      exit 1
      ;;
  esac
done

ARCHIVE_PATHS=$(find "${TARGET_ROOT}" -type d -name archive -prune)

if [ -z "${ARCHIVE_PATHS}" ]; then
  echo "No archive directories found under ${TARGET_ROOT}"
  exit 0
fi

while IFS= read -r ARCHIVE_DIR; do
  echo "Processing ${ARCHIVE_DIR}"
  if [ "${COMPRESS}" = true ]; then
    find "${ARCHIVE_DIR}" -type f -mtime +"${RETENTION_DAYS}" -print0 | while IFS= read -r -d '' FILE; do
      gzip -f "${FILE}"
      echo "Compressed ${FILE}"
    done
  else
    find "${ARCHIVE_DIR}" -type f -mtime +"${RETENTION_DAYS}" -print -delete
  fi
done <<< "${ARCHIVE_PATHS}"

echo "Archive cleanup complete"

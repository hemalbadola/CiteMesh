#!/usr/bin/env bash
# sync_subfolder.sh
# Purpose: Sync contributor subfolders into a central review directory for integration checks.
# Usage: ./sync_subfolder.sh [-d DESTINATION_PATH] [-n]
# Dependencies: bash 4+, rsync
# Flags:
#   -d Specify destination root (default: ./integration_sync)
#   -n Dry run mode; prints actions without copying files.
set -euo pipefail

DESTINATION="$(pwd)/integration_sync"
DRY_RUN=false

while getopts ":d:n" opt; do
  case "$opt" in
    d)
      DESTINATION="${OPTARG}"
      ;;
    n)
      DRY_RUN=true
      ;;
    *)
      echo "Usage: $0 [-d DESTINATION_PATH] [-n]" >&2
      exit 1
      ;;
  esac
done

mkdir -p "${DESTINATION}"

sync_folder() {
  local SRC_FOLDER="$1"
  local DEST_FOLDER="${DESTINATION}/$(basename "${SRC_FOLDER}")"
  mkdir -p "${DEST_FOLDER}"
  local RSYNC_FLAGS="-av"
  if [ "${DRY_RUN}" = true ]; then
    RSYNC_FLAGS="-avn"
  fi
  rsync ${RSYNC_FLAGS} --delete "${SRC_FOLDER}/" "${DEST_FOLDER}/"
}

for CONTRIBUTOR in naincy maaz hemal ayush; do
  if [ -d "${CONTRIBUTOR}" ]; then
    sync_folder "${CONTRIBUTOR}"
  else
    echo "Warning: missing folder ${CONTRIBUTOR}, skipping" >&2
  fi
done

echo "Sync complete -> ${DESTINATION}"

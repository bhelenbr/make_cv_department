#!/usr/bin/env bash

# Usage: copy_xlsx_tree.sh SOURCE_DIR DEST_DIR

set -euo pipefail

SRC="$1"
DEST="$2"
ENDING="$3"

# Ensure source exists
if [[ ! -d "$SRC" ]]; then
    echo "Source directory does not exist: $SRC"
    exit 1
fi

# Create destination if it doesn't exist
mkdir -p "$DEST"

# Find and copy all .xlsx files
find "$SRC" -type f -name "*.${ENDING}" | while read -r file; do
    # Compute relative path
    rel_path="${file#$SRC/}"

    # Destination path
    dest_file="$DEST/$rel_path"

    # Create destination directory
    mkdir -p "$(dirname "$dest_file")"

    # Copy file
    cp -p "$file" "$dest_file"
done

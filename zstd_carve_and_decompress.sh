#!/bin/bash
# Usage: bash zstd_carve_and_decompress.sh <file> [byte_offset]
FILE="$1"
OFFSET="${2:-0}"

if [ "$OFFSET" = "0" ]; then
    echo "Trying direct decompress..."
    zstd -d "$FILE" -o recovered_output 2>&1
    if [ -s recovered_output ]; then
        echo "Success:"
        cat recovered_output
        exit 0
    fi
fi

echo "Carving from offset $OFFSET..."
dd if="$FILE" of=carved.zst bs=1 skip="$OFFSET" 2>/dev/null
zstd -d carved.zst -o recovered_output
cat recovered_output

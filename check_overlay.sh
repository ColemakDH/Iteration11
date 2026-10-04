#!/bin/bash
# Checks if binwalk caught a jffs2/ubifs overlay separately from squashfs roots
echo "=== Full binwalk scan of original firmware (re-check for jffs2/ubifs) ==="
binwalk openwrt-mt300n-v2-4.3.25-0318-1742298825.bin

echo
echo "=== Any jffs2/ubifs directories already extracted? ==="
find . -iname "*jffs2*" -o -iname "*ubifs*" -o -iname "*overlay*" 2>/dev/null

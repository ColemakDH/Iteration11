#!/bin/bash
# Run from the directory containing suspect_extracted/ and stock_extracted/

echo "=== uci-defaults script (re-check, 'ovpn' in the name is a lead) ==="
cat suspect_extracted/*/etc/uci-defaults/lb_fix_ovpn_dns_leak_keep 2>/dev/null

echo
echo "=== OpenVPN config files ==="
find suspect_extracted -path "*openvpn*" -type f -exec echo "--- {} ---" \; -exec cat {} \;

echo
echo "=== UCI network config for vpn/tunnel/remote entries ==="
grep -A5 -i "vpn\|tunnel\|remote" suspect_extracted/*/etc/config/network 2>/dev/null
cat suspect_extracted/*/etc/config/openvpn 2>/dev/null

echo
echo "=== Dropbear/SSH authorized_keys diff (backdoor access check) ==="
diff suspect_extracted/*/etc/dropbear/authorized_keys stock_extracted/*/etc/dropbear/authorized_keys 2>/dev/null
cat suspect_extracted/*/etc/dropbear/authorized_keys 2>/dev/null
find suspect_extracted -path "*.ssh/authorized_keys" -exec cat {} \;

echo
echo "=== zstd-compressed files by type ==="
find suspect_extracted -type f -exec sh -c 'file "$1" | grep -qi "zstd\|Zstandard\|compress" && echo "$1"' _ {} \;

echo
echo "=== Raw zstd magic bytes (28 B5 2F FD) anywhere on disk ==="
find suspect_extracted -type f -exec sh -c 'xxd -l 4 "$1" 2>/dev/null | grep -q "28b5 2ffd" && echo "ZSTD: $1"' _ {} \;

echo
echo "=== Log/tmp/var locations ==="
find suspect_extracted -path "*/var/log/*" -o -path "*/tmp/*" -o -iname "*.log" -o -iname "*.cap*" -o -iname "*.dump" 2>/dev/null

echo
echo "=== netmgrd init.d script (re-check for output/log flags) ==="
find suspect_extracted -path "*/etc/init.d/*netmgrd*" -exec cat {} \;

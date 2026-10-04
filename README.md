# CTF Run Sheet

## Pre-session: make git repo PUBLIC
Private repos need auth a fresh liveboot box won't have.

## Files needed in root directory
- `openwrt-mt300n-v2-4.3.25-0318-1742298825.bin`
- `stock_firmware.bin`
- `codex`

## Scripts needed
netmgrd_followup.sh
check_overlay.sh
zstd_carve_and_decompress.sh
deadfish_ry_atomic.py
deadfish_fresh.py
solve.py
ssh_scratch_log.sh
ssh_key_comment_test.sh

---

## Setup
```bash
sudo apt update
sudo apt install -y binwalk squashfs-tools jefferson ent zstd
pip3 install ubi_reader --break-system-packages
```

---

## 1. OpenWrt — recover communications

If not already extracted:
```bash
binwalk -e openwrt-mt300n-v2-4.3.25-0318-1742298825.bin
mv _openwrt-mt300n-v2-4.3.25-0318-1742298825.bin.extracted suspect_extracted
binwalk -e stock_firmware.bin
mv _stock_firmware.bin.extracted stock_extracted
```

```bash
bash check_overlay.sh
```
Confirms whether binwalk caught a jffs2/ubifs overlay separately — runtime-written data (actual captures) would live there, not in read-only squashfs. Extract explicitly with `jefferson`/`ubireader_extract_images` if found and not already pulled out.

```bash
bash netmgrd_followup.sh
```
Priority order to read:
1. **OpenVPN config/uci-defaults content** — "ovpn" in the script name is a real lead toward a tunnel/remote server address
2. **authorized_keys diff** — backdoor SSH access is itself a comms channel
3. zstd checks, log/tmp paths, init.d flags (as before)

If a zstd blob or offset turns up:
```bash
bash zstd_carve_and_decompress.sh <file> [offset]
```

---

## 2. Deadfish (`codex`)

**Run this first** — directly motivated by your confirmed r-always-followed-by-y finding:
```bash
python3 deadfish_ry_atomic.py
```
Treats `ry` as one atomic output+reset token, `>` as stripped noise, tests all 6 d/s/i permutations as inc/dec/square.

If nothing scores well:
```bash
python3 deadfish_fresh.py
```
Three more hypotheses: base-3, binary+separator, Morse code (most promising given your variable group lengths).

Final fallback:
```bash
python3 solve.py codex --deep
```

---

## 3. SSH Portal

**Username channel is likely dead** (SSH restricts login characters) — don't prioritize.

**New untested surface — SSH key comment field** (the challenge specifically mentions "any SSH key is accepted," which is a hint worth taking seriously):
```bash
bash ssh_key_comment_test.sh
```
Watch for the comment payload reflected anywhere before/during portal load.

**Primary surface — the `/` filter box:**
```bash
bash ssh_scratch_log.sh
```
Press `/`, test payloads one at a time:
F5: {{printf "%#v" .}}
F6: {{.Query}}
F7: {{.Payload}}

**Also check inside a posting's detail view** (press Enter on one) for any extra input prompts (e.g. "apply to this job") — richer injection surface than the filter if it exists.

**Check for a help/footer screen** — look at the bottom of the TUI for additional keybindings beyond arrows/Enter/Esc/q//.

Re-read all 4 postings between tests; TEE/attestation and "internal ops on loopback" language are likely thematic hints about the Vault's sealed state.

---

## Priority order
OpenWrt (ovpn/authorized_keys leads are strong) → Deadfish (ry-atomic is the sharpest lead yet) → SSH Portal (key-comment + filter box).

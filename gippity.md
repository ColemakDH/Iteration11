# `netmgrd` CTF Quick Analysis

Goal: find a flag likely formatted like:

```text
tribectf{...}
```

Run these steps in order.

---

## 1. Identify the File

```bash
file netmgrd
sha256sum netmgrd
ls -lh netmgrd
```

If it says **ELF**, continue.

```bash
readelf -h netmgrd
readelf -S netmgrd
```

---

## 2. Dump Strings With Offsets

```bash
strings -a -t x -n 4 netmgrd | tee strings.txt
```

Search for obvious clues:

```bash
grep -iE 'tribe|ctf|flag|zstd|password|secret|token|root' strings.txt
```

Check UTF-16 strings too:

```bash
strings -a -e l -t x netmgrd > strings_utf16le.txt
strings -a -e b -t x netmgrd > strings_utf16be.txt

grep -iE 'tribe|ctf|flag|secret' strings_utf16le.txt strings_utf16be.txt
```

---

## 3. Find the Weird Strings

Search for the strings we already saw:

```bash
grep -E 'jrml|wfUD|msM|GLc|T3c|MIc|TrB|erB|rpc' strings.txt
```

Pay attention to the offsets.

If all of these appear very close together, they may just be machine-code bytes accidentally interpreted as ASCII.

---

## 4. Inspect the Bytes Around a Weird String

Example output:

```text
123abc <GLc$P
```

Inspect around it:

```bash
xxd -s 0x123a00 -l 512 netmgrd
```

Or:

```bash
hexdump -C -s $((0x123abc - 128)) -n 512 netmgrd
```

Replace the address with the real offset.

---

## 5. Check for Compression

Run:

```bash
binwalk netmgrd
```

If available:

```bash
binwalk -e netmgrd
```

Check extracted files:

```bash
find _netmgrd.extracted -type f 2>/dev/null
```

Search extracted data:

```bash
find _netmgrd.extracted -type f -exec sh -c '
echo "===== $1 ====="
strings -a "$1" | grep -iE "tribe|ctf|flag|secret"
' sh {} \;
```

---

## 6. Check Specifically for Zstd

Zstd magic bytes are:

```text
28 b5 2f fd
```

Search:

```bash
grep -oba $'\x28\xb5\x2f\xfd' netmgrd
```

If you get something like:

```text
123456:
```

Extract from that decimal offset:

```bash
dd if=netmgrd of=possible.zst bs=1 skip=123456 status=none
```

Then:

```bash
file possible.zst
zstd -d possible.zst -o decompressed.bin
```

Search it:

```bash
strings -a decompressed.bin | grep -iE 'tribe|ctf|flag'
```

Or:

```bash
strings -a decompressed.bin | less
```

---

## 7. Check Other Compression Formats

```bash
grep -oba $'\x1f\x8b\x08' netmgrd
grep -oba $'\xfd\x37\x7a\x58\x5a\x00' netmgrd
grep -oba $'\x42\x5a\x68' netmgrd
grep -oba $'\x50\x4b\x03\x04' netmgrd
```

These indicate roughly:

```text
gzip
xz
bzip2
zip
```

Extract using:

```bash
dd if=netmgrd of=blob.bin bs=1 skip=OFFSET status=none
file blob.bin
```

---

## 8. Check Whether Weird Strings Are Machine Code

Disassemble:

```bash
objdump -d -M intel netmgrd > disasm.txt
```

If a weird string was near address `0x123abc`:

```bash
objdump -d -M intel \
  --start-address=0x123a00 \
  --stop-address=0x123c00 \
  netmgrd
```

If that region shows normal valid instructions, the weird strings like:

```text
<GLc$P
<T3c$T
<cpc$x
```

are probably **not encoded text**.

They're likely just instruction bytes that `strings` happened to print.

---

## 9. Search Raw Binary for Flag Prefix

```bash
grep -oba 'tribectf' netmgrd
grep -oba 'tribe' netmgrd
grep -oba 'ctf{' netmgrd
grep -ioba 'tribectf' netmgrd
```

---

## 10. Search for Single-Byte XOR Flag

Run:

```bash
python3 - <<'PY'
data = open("netmgrd", "rb").read()
target = b"tribectf{"

for key in range(256):
    encoded = bytes(c ^ key for c in target)
    pos = data.find(encoded)

    if pos != -1:
        print("FOUND POSSIBLE XOR")
        print("Key:", hex(key))
        print("Offset:", hex(pos))

        chunk = data[pos:pos+100]
        print(bytes(c ^ key for c in chunk))
PY
```

If you see:

```text
tribectf{something}
```

you probably found it.

---

## 11. Check Imports for Useful Functions

```bash
nm -D netmgrd 2>/dev/null | grep -Ei 'zstd|zlib|inflate|decompress|strcmp|memcmp|crypt|aes|xor'
```

Also:

```bash
objdump -T netmgrd 2>/dev/null | grep -Ei 'zstd|inflate|strcmp|memcmp|crypt'
```

Important hits include:

```text
ZSTD_decompress
memcmp
strcmp
```

---

## 12. Check Linked Libraries

```bash
ldd netmgrd 2>/dev/null
```

Interesting libraries:

```text
libzstd
libcrypto
libssl
liblzma
libz
```

If `libzstd` appears, the zstd theory gets much stronger.

---

# GDB Method

If static analysis doesn't reveal the flag, use GDB.

```bash
gdb ./netmgrd
```

Inside GDB:

```gdb
set disassembly-flavor intel
break strcmp
break memcmp
run
```

When `strcmp` breaks on x86-64 Linux:

```gdb
x/s $rdi
x/s $rsi
```

For `memcmp`:

```gdb
p $rdx
x/64bx $rdi
x/64bx $rsi
```

Continue:

```gdb
continue
```

Keep checking each comparison.

---

# GDB + Zstd

If the binary imports `ZSTD_decompress`:

```gdb
break ZSTD_decompress
run
```

Arguments on x86-64 Linux are roughly:

```text
rdi = destination
rsi = destination capacity
rdx = compressed source
rcx = compressed size
```

Save the output pointer:

```gdb
set $dst = $rdi
```

Inspect compressed input:

```gdb
p $rcx
x/64bx $rdx
```

Let decompression finish:

```gdb
finish
```

Inspect decompressed data:

```gdb
x/200bx $dst
x/s $dst
```

Also try:

```gdb
x/20s $dst
```

Search visually for:

```text
tribectf{
```

---

# Fastest Checklist

If you're running out of time, run only this:

```bash
file netmgrd

strings -a -t x -n 4 netmgrd > strings.txt

grep -iE 'tribe|ctf|flag|zstd|secret' strings.txt

grep -E 'jrml|wfUD|msM|GLc|T3c|MIc|TrB|erB|rpc' strings.txt

binwalk netmgrd

grep -oba $'\x28\xb5\x2f\xfd' netmgrd

ldd netmgrd

nm -D netmgrd 2>/dev/null | grep -Ei 'zstd|memcmp|strcmp|crypt'
```

Then run the XOR script from Step 10.

---

# Key Interpretation

The weird strings:

```text
<TrB$,
<erB$@
<c/c$D
<vic$H
<GLc$P
<T3c$T
<cpc$x
<moc$|
<MIc$l
```

probably **should not be directly concatenated or decoded as text**.

The repeated:

```text
<
$
B
c
```

pattern strongly suggests they may be bytes from executable instructions.

The three strings:

```text
jrml[Q
wfUD3"
msM|&.
```

look more like random/high-entropy binary data.

Focus on:

```text
1. zstd/compression magic
2. imported decompression functions
3. memcmp/strcmp
4. XOR-obfuscated tribectf{
5. runtime decompressed buffers in GDB
```

Best bet if everything else fails:

```text
break ZSTD_decompress
break memcmp
break strcmp
```

and inspect the buffers.

That is where the binary may stop being a mysterious little asshole and just hand you the damn flag.

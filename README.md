# IMEI Tools

Five Python scripts for inspecting Redmi A5 FIXNV partition dumps, extracting IMEI records, and converting between 15-digit IMEIs and their eight-byte binary representation. All image operations are read-only.

## Quick start on Windows

Use Python 3.8 or later. Extract all five scripts into the same folder and place `l_fixnv1.img` and `l_fixnv2.img` alongside them. The scripts use only the Python standard library.

```bat
cd /d D:\imeitools
py -3 magichcheck.py l_fixnv1.img l_fixnv2.img
py -3 getimei.py l_fixnv1.img
```

`getimei.py` masks all but the last four digits by default. To display the full values, run:

```bat
py -3 getimei.py --show-full l_fixnv1.img
```

The updated script also accepts `--showfull`. If an older copy reports `unrecognized arguments: --showfull`, use `--show-full`.

## Commands

| Script | Example | What it does |
|---|---|---|
| `getimei.py` | `py -3 getimei.py l_fixnv1.img` | Lists known IMEI records by NV item ID and absolute payload offset. |
| `magichcheck.py` | `py -3 magichcheck.py l_fixnv1.img l_fixnv2.img` | Verifies the FIXNV magic, declared length, payload checksum, record boundaries, and end marker. Returns a nonzero exit code if any image fails. |
| `magictool.py` | `py -3 magictool.py l_fixnv1.img --list` | Prints header fields and lists every NV item with its offset and length. Omit `--list` for the header alone. |
| `encode.py` | `py -3 encode.py 490154203237518` | Validates the 15 digits and prints the packed payload as hex. |
| `decode.py` | `py -3 decode.py 4A 09 51 24 30 32 57 81` | Decodes eight hex bytes and verifies the IMEI check digit. Also accepts joined hex such as `4A09512430325781`. |

## IMEI encoding

The first byte holds digit 1 in its high nibble and the marker `A` in its low nibble. For each of the remaining seven bytes, read the low nibble first and the high nibble second. The final high nibble holds digit 15, the Luhn check digit.

```text
Packed bytes    4A  09  51  24  30  32  57  81
Decoded digits   4  90  15  42  03  23  75  18
IMEI             490154203237518
```

## Verified Redmi A5 dump layout

The two tested FIXNV images were byte-for-byte identical. Each contained 586 NV records and had a payload checksum of `0xF329`.

| NV item ID | IMEI payload offset | Masked ending |
|---|---:|---|
| `0x0005` | `0x000016F4` | `…0242` |
| `0x0179` | `0x0001533C` | `…0259` |
| `0x0186` | `0x00015348` | `…6638` |
| `0x01E4` | `0x00016110` | `…6646` |

These offsets apply to the tested dumps. `getimei.py` walks the record table by item ID, so it can find the records at different offsets in another image with the same layout. To identify which entries your phone reports, compare their endings with the values displayed by `*#06#`. NV item order alone does not establish a SIM-slot mapping.

## Troubleshooting

- **`ModuleNotFoundError`** — Keep all five `.py` files together. The scripts import functions from one another.
- **`ext filesystem image`** — The supplied `prodnv.img` is an ext4 filesystem. Use `l_fixnv1.img` or `l_fixnv2.img` with the FIXNV tools.
- **Checksum mismatch** — `magichcheck.py` reports both the stored and computed checksums. Check each backup separately. A valid Luhn digit verifies an individual IMEI, while the FIXNV checksum covers the declared NV payload.

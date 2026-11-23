"""Extract known IMEI records from a FIXNV image by item ID."""
import argparse
from pathlib import Path

from decode import decode_imei
from magictool import read_header, records

IMEI_IDS = {0x0005, 0x0179, 0x0186, 0x01E4}


def get_imeis(data):
    header = read_header(data)
    found = []
    for item, offset, size in records(data, header):
        if item in IMEI_IDS:
            try:
                imei = decode_imei(data[offset:offset + size])
            except ValueError as exc:
                raise ValueError(f"item 0x{item:04X} at 0x{offset:X}: {exc}") from exc
            found.append((item, offset, imei))
    if not found:
        raise ValueError("no known IMEI records found")
    return found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--show-full", action="store_true", help="show all 15 digits")
    args = parser.parse_args()
    try:
        rows = get_imeis(args.image.read_bytes())
        print("Item ID    Data offset    IMEI")
        for item, offset, imei in rows:
            display = imei if args.show_full else "*" * 11 + imei[-4:]
            print(f"0x{item:04X}     0x{offset:08X}     {display}")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

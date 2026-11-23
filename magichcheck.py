"""Check FIXNV magic, declared length, payload checksum and record boundaries."""
import argparse
import sys
from pathlib import Path

from magictool import payload_checksum, read_header, records


def check_image(path):
    data = path.read_bytes()
    header = read_header(data)
    checksum = payload_checksum(data, header)
    if header.checksum != checksum:
        raise ValueError(f"stored checksum 0x{header.checksum:04X}, computed 0x{checksum:04X}")
    count = sum(1 for _ in records(data, header))
    return f"PASS  checksum 0x{checksum:04X}, {count} records"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()
    status = 0
    for path in args.images:
        try:
            print(f"{path}: {check_image(path)}")
        except (OSError, ValueError) as exc:
            print(f"{path}: FAIL  {exc}", file=sys.stderr)
            status = 1
    sys.exit(status)

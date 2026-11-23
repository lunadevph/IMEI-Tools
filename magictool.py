"""Inspect a FIXNV header and optionally list NV item IDs, offsets and lengths."""
import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

HEADER_SIZE = 0x200
RECORDS_START = HEADER_SIZE + 4
MAGIC = 0x4E56


@dataclass
class Header:
    magic: int
    length: int
    checksum: int
    field_0c: int


def read_header(data):
    if len(data) < HEADER_SIZE:
        raise ValueError("truncated FIXNV header")
    header = Header(*struct.unpack_from("<4I", data))
    if header.magic != MAGIC:
        if data[0x438:0x43A] == b"\x53\xef":
            raise ValueError("ext filesystem image; supply l_fixnv1.img or l_fixnv2.img")
        raise ValueError(f"unexpected FIXNV magic 0x{header.magic:08X}")
    if header.length < 6 or header.length > len(data) - HEADER_SIZE:
        raise ValueError("declared NV payload length is outside image bounds")
    return header


def records(data, header):
    """Yield (item ID, absolute payload offset, payload size) until the end marker."""
    end = HEADER_SIZE + header.length
    offset = RECORDS_START
    while offset + 2 <= end:
        item_id, = struct.unpack_from("<H", data, offset)
        if item_id == 0xFFFF:
            return
        if offset + 4 > end:
            raise ValueError(f"truncated item header at 0x{offset:X}")
        size, = struct.unpack_from("<H", data, offset + 2)
        value = offset + 4
        if value + size > end:
            raise ValueError(f"item 0x{item_id:04X} exceeds the declared payload")
        yield item_id, value, size
        offset = (value + size + 3) & ~3
    raise ValueError("missing NV record terminator")


def payload_checksum(data, header):
    block = memoryview(data)[HEADER_SIZE:HEADER_SIZE + header.length]
    even_length = len(block) & ~1
    total = sum(word for word, in struct.iter_unpack("<H", block[:even_length]))
    if even_length != len(block):
        total += block[-1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--list", action="store_true", help="list all NV record headers")
    args = parser.parse_args()
    try:
        data = args.image.read_bytes()
        header = read_header(data)
        print(f"Magic: 0x{header.magic:08X}    Payload length: 0x{header.length:X}")
        print(f"Stored checksum: 0x{header.checksum:04X}    Header field 0x0C: 0x{header.field_0c:X}")
        print(f"Payload starts at 0x{HEADER_SIZE:X}; record table starts at 0x{RECORDS_START:X}")
        if args.list:
            print("Item ID    Data offset    Length")
            for item, value, size in records(data, header):
                print(f"0x{item:04X}     0x{value:08X}     {size}")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

"""Decode an eight-byte FIXNV IMEI payload given as hex."""
import argparse


def validate_imei(digits):
    if len(digits) != 15 or not digits.isascii() or not digits.isdigit():
        raise ValueError("expected exactly 15 decimal digits")
    total = 0
    for index, char in enumerate(digits):
        value = int(char)
        if index % 2:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    if total % 10:
        raise ValueError("IMEI failed its Luhn check")


def decode_imei(payload):
    if len(payload) != 8:
        raise ValueError("expected an eight-byte payload")
    if payload[0] & 15 != 0xA:
        raise ValueError("expected IMEI marker A in the first low nibble")
    digits = [payload[0] >> 4]
    for byte in payload[1:]:
        digits.extend((byte & 15, byte >> 4))
    if max(digits) > 9:
        raise ValueError("payload contains a nondecimal IMEI digit")
    result = "".join(map(str, digits))
    validate_imei(result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hex_bytes", nargs="+", help="eight hex bytes, spaced or joined")
    args = parser.parse_args()
    try:
        print(decode_imei(bytes.fromhex(" ".join(args.hex_bytes))))
    except ValueError as exc:
        parser.exit(1, f"error: {exc}\n")

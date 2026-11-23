"""Print the eight-byte FIXNV payload for a 15-digit IMEI."""
import argparse

from decode import validate_imei


def encode_imei(digits):
    validate_imei(digits)
    payload = bytearray([(int(digits[0]) << 4) | 0xA])
    for i in range(1, 15, 2):
        payload.append(int(digits[i]) | (int(digits[i + 1]) << 4))
    return bytes(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imei", help="15 digits including the check digit")
    args = parser.parse_args()
    try:
        print(encode_imei(args.imei).hex(" ").upper())
    except ValueError as exc:
        parser.exit(1, f"error: {exc}\n")

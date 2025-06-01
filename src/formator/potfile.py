import binascii
import logging

def decode_hexed(maybe_hexed: str) -> str:
    if maybe_hexed.startswith('$HEX[') and maybe_hexed.endswith(']'):
        hex_str = maybe_hexed[5:-1]
        try:
            return binascii.unhexlify(hex_str).decode('utf-8', errors='replace')
        except Exception as e:
            logging.error(f"Failed to decode hex password: {hex_str} ({e})")
            return maybe_hexed
    return maybe_hexed

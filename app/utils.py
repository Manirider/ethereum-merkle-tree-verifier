def hex_to_bytes(hex_str: str) -> bytes:
    """Convert a hex string to bytes."""
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    # Pad to even length if needed
    if len(hex_str) % 2 != 0:
        hex_str = "0" + hex_str
    return bytes.fromhex(hex_str)


def bytes_to_hex(b: bytes) -> str:
    """Convert bytes to a 0x-prefixed hex string."""
    return "0x" + b.hex()

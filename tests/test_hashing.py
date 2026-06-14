from app.hashing import hash_pair, keccak256_hash, sha256_hash
from app.utils import hex_to_bytes


def test_sha256_hash():
    data = b"hello world"
    # echo -n "hello world" | sha256sum -> b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    h = sha256_hash(data)
    assert len(h) == 32
    assert h.hex() == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_keccak256_hash():
    data = b"hello world"
    # Keccak256 of "hello world" -> 47173285a8d7341e5e972fc677286384f802f8ef42a5ec5f03bbfa254cb01fad
    h = keccak256_hash(data)
    assert len(h) == 32
    assert h.hex() == "47173285a8d7341e5e972fc677286384f802f8ef42a5ec5f03bbfa254cb01fad"


def test_hash_pair():
    left = b"1" * 32
    right = b"2" * 32
    parent = hash_pair(left, right, keccak256_hash)
    assert len(parent) == 32
    assert parent == keccak256_hash(left + right)


def test_hex_to_bytes():

    # Normal hex
    assert hex_to_bytes("0xabcd") == b"\xab\xcd"
    # Hex without 0x prefix
    assert hex_to_bytes("abcd") == b"\xab\xcd"
    # Odd length hex (gets padded with leading 0)
    assert hex_to_bytes("abc") == b"\x0a\xbc"
    assert hex_to_bytes("0xabc") == b"\x0a\xbc"


def test_bytes_to_hex():
    from app.utils import bytes_to_hex

    assert bytes_to_hex(b"\xab\xcd") == "0xabcd"

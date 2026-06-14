import hashlib
from collections.abc import Callable

from web3 import Web3

# Type alias for hash functions: takes bytes, returns 32 bytes
HashFunction = Callable[[bytes], bytes]


def sha256_hash(data: bytes) -> bytes:
    """
    Simplified hashing mode using standard SHA-256.

    Args:
        data: The input bytes.

    Returns:
        32-byte SHA-256 hash.
    """
    return hashlib.sha256(data).digest()


def keccak256_hash(data: bytes) -> bytes:
    """
    Real Ethereum hashing mode using Keccak-256.

    Args:
        data: The input bytes.

    Returns:
        32-byte Keccak-256 hash.
    """
    return Web3.keccak(data)


def hash_pair(
    left: bytes, right: bytes, hash_fn: HashFunction = keccak256_hash
) -> bytes:
    """
    Hash a pair of sibling nodes. In Ethereum and standard Merkle Trees,
    the parent hash is Hash(left + right).

    Args:
        left: Left child hash (32 bytes).
        right: Right child hash (32 bytes).
        hash_fn: The hashing function to use (default: Keccak-256).

    Returns:
        The 32-byte parent hash.
    """
    return hash_fn(left + right)

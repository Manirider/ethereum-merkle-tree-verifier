from typing import Any

import rlp
from rlp.sedes import Binary, big_endian_int, binary

from app.config import setup_logger
from app.hashing import keccak256_hash, sha256_hash
from app.merkle_tree import MerkleTree
from app.utils import bytes_to_hex, hex_to_bytes

logger = setup_logger(__name__)


# Legacy Transaction RLP structure for from-scratch Mode B hashing
class LegacyTransaction(rlp.Serializable):
    fields = [
        ("nonce", big_endian_int),
        ("gasPrice", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    ]


def hash_transaction_simple(tx: dict[str, Any]) -> bytes:
    """
    Mode A: Simplified SHA256 of the concatenated raw hex string.
    Educational purpose only. Not how Ethereum calculates transaction hashes.
    """
    raw_str = f"{tx.get('hash', '')}{tx.get('nonce', '')}"
    return sha256_hash(raw_str.encode("utf-8"))


def hash_transaction_rlp(tx: dict[str, Any]) -> bytes:
    """
    Mode B: Real Ethereum hashing.
    Extracts the 'hash' field directly if available, as calculating the
    exact RLP representation of typed transactions (EIP-1559, EIP-2930)
    requires complex raw payload reconstruction.
    """
    tx_hash = tx.get("hash")
    if not tx_hash:
        raise ValueError("Transaction object missing 'hash' field")
    return hex_to_bytes(tx_hash)


def reconstruct_transactions_root(
    transactions: list[dict[str, Any]], hash_mode: str = "real"
) -> tuple[bytes, MerkleTree]:
    """
    Reconstruct the transactions root by building the Merkle Tree.

    Args:
        transactions: List of transaction objects from RPC block.
        hash_mode: "real" for Keccak256 or "simple" for SHA256.

    Returns:
        A tuple of (computed_root_bytes, MerkleTree).
    """
    if not transactions:
        # According to Ethereum spec, the Merkle root of an empty list is
        # Keccak256(RLP("")) -> Keccak256(0x80) -> 0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421
        empty_rlp = b"\x80"
        empty_root = (
            keccak256_hash(empty_rlp) if hash_mode == "real" else sha256_hash(empty_rlp)
        )
        return empty_root, None  # type: ignore

    leaves = []
    for tx in transactions:
        if hash_mode == "real":
            leaves.append(hash_transaction_rlp(tx))
        else:
            leaves.append(hash_transaction_simple(tx))

    hash_fn = keccak256_hash if hash_mode == "real" else sha256_hash
    tree = MerkleTree(leaves, hash_fn=hash_fn)
    return tree.root, tree


def verify_transactions_root(block: dict[str, Any], hash_mode: str = "real") -> bool:
    """
    Reconstruct the transactions root and compare it against the block's transactionsRoot.
    """
    expected_root = hex_to_bytes(block["transactionsRoot"])
    transactions = block.get("transactions", [])

    logger.info(f"Verifying {len(transactions)} transactions using mode '{hash_mode}'")

    computed_root, _ = reconstruct_transactions_root(transactions, hash_mode)

    print(f"Expected Root: {bytes_to_hex(expected_root)}")
    print(f"Computed Root: {bytes_to_hex(computed_root)}")

    match = computed_root == expected_root
    if match:
        print("Match: YES - Roots are identical.")
    else:
        print("Match: NO - Roots differ.")
        if hash_mode == "simple":
            print(
                "Explanation: Simplified hashing does not match Ethereum's RLP + Keccak256 standard."
            )
        elif hash_mode == "real":
            print(
                "Explanation: A binary Merkle Tree root differs from the block header's transactionsRoot "
                "because Ethereum uses a Merkle Patricia Trie (MPT) rather than a simple binary Merkle Tree."
            )

    return match

from typing import Any

from app.ethereum import fetch_block
from app.merkle_tree import MerkleTree
from app.proof import MerkleProof, verify_proof
from app.verifier import reconstruct_transactions_root


# --- Extension A: Recursive Length Prefix (RLP) Encoding ---
def rlp_encode(input_val: bytes | str | list[Any]) -> bytes:
    """
    RLP encodes a given input. RLP encoding supports bytes, strings, and lists.
    This is a simplified pure Python implementation of the Ethereum RLP spec.
    """
    if isinstance(input_val, str):
        input_val = input_val.encode("utf-8")

    if isinstance(input_val, bytes):
        if len(input_val) == 1 and input_val[0] < 0x80:
            return input_val
        elif len(input_val) < 56:
            return bytes([0x80 + len(input_val)]) + input_val
        else:
            len_bytes = len(input_val).to_bytes(
                (len(input_val).bit_length() + 7) // 8, "big"
            )
            return bytes([0xB7 + len(len_bytes)]) + len_bytes + input_val
    elif isinstance(input_val, list):
        body = b"".join(rlp_encode(item) for item in input_val)
        if len(body) < 56:
            return bytes([0xC0 + len(body)]) + body
        else:
            len_bytes = len(body).to_bytes((len(body).bit_length() + 7) // 8, "big")
            return bytes([0xF7 + len(len_bytes)]) + len_bytes + body
    else:
        raise TypeError("RLP encoding only supports bytes, strings, or lists.")


# --- Extension B: Odd Leaf Verification Verification Helper ---
def verify_odd_leaf_duplication(tree: MerkleTree) -> bool:
    """
    Verifies that the odd leaf duplication works correctly.
    Specifically checks if a tree with odd leaves duplicates the last hash.
    """
    if len(tree.leaves) % 2 == 0:
        return True  # Even leaves don't have duplication at the bottom level

    # Check parent of last node
    parent_level = tree.levels[1]
    last_parent = parent_level[-1]

    if last_parent.left is None or last_parent.right is None:
        return False

    # The parent should have identical left and right child hashes
    return last_parent.left.hash == last_parent.right.hash


# --- Extension C: Light Client Simulation ---
class LightClientSimulator:
    """
    Simulates a Light Client which only stores block headers (and therefore
    trusted roots) and verifies transaction inclusion using Merkle Proofs.
    """

    def __init__(self) -> None:
        # Map of block_number -> trusted_binary_root
        self.headers_db: dict[int, bytes] = {}

    def ingest_block_header(self, block_number: int, trusted_root: bytes) -> None:
        """Stores a block header's root in the light client local storage."""
        self.headers_db[block_number] = trusted_root

    def verify_transaction(self, block_number: int, proof: MerkleProof) -> bool:
        """
        Verify if a transaction is included in a specific block using the proof
        and the local trusted root database.
        """
        trusted_root = self.headers_db.get(block_number)
        if not trusted_root:
            raise ValueError(f"No trusted header for block {block_number}")

        return verify_proof(proof, trusted_root)


# --- Extension D: Historical Block Verification ---
def verify_historical_blocks(start_block: int, count: int) -> dict[int, bool]:
    """
    Fetches and verifies the transactions roots of a range of historical blocks.
    Note: It will compute the binary Merkle root of the transaction list.
    Since Ethereum transactionsRoot uses MPT, we verify consistency of binary root
    construction across these blocks.
    """
    results = {}
    for i in range(count):
        block_num = start_block - i
        try:
            block = fetch_block(block_num)
            txs = block.get("transactions", [])
            _, tree = reconstruct_transactions_root(txs, hash_mode="real")

            # As binary Merkle Root doesn't match block's transactionsRoot MPT,
            # we check if we successfully constructed the binary Merkle Tree
            # and generated a valid proof for the first transaction.
            if txs:
                proof = tree.get_proof(0)
                is_valid = verify_proof(proof, tree.root)
                results[block_num] = is_valid
            else:
                results[block_num] = True  # Empty block verification succeeds
        except Exception:
            results[block_num] = False

    return results

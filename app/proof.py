from dataclasses import dataclass

from app.hashing import HashFunction, hash_pair, keccak256_hash
from app.utils import bytes_to_hex


@dataclass(frozen=True)
class MerkleProof:
    """
    Represents an inclusion proof in a Merkle Tree.
    """

    target_hash: bytes
    target_index: int
    # List of tuples (sibling_hash, is_left_sibling)
    path: list[tuple[bytes, bool]]

    def __str__(self) -> str:
        s = f"MerkleProof for leaf at index {self.target_index}:\n"
        s += f"  Target: {bytes_to_hex(self.target_hash)}\n"
        for i, (sibling, is_left) in enumerate(self.path):
            side = "LEFT " if is_left else "RIGHT"
            s += f"  Step {i}: {side} -> {bytes_to_hex(sibling)}\n"
        return s


def verify_proof(
    proof: MerkleProof,
    expected_root: bytes,
    hash_fn: HashFunction = keccak256_hash,
) -> bool:
    """
    Standalone verification of a Merkle proof.
    Recomputes the root hash by walking up the path and checks against expected_root.

    Args:
        proof: The MerkleProof object.
        expected_root: The expected 32-byte root hash of the tree.
        hash_fn: The hash function to use (default Keccak-256).

    Returns:
        True if the proof is valid and the recomputed root matches expected_root.
    """
    if not proof.target_hash:
        return False

    current_hash = proof.target_hash

    for sibling_hash, is_left_sibling in proof.path:
        if is_left_sibling:
            current_hash = hash_pair(sibling_hash, current_hash, hash_fn)
        else:
            current_hash = hash_pair(current_hash, sibling_hash, hash_fn)

    return current_hash == expected_root

from dataclasses import dataclass
from typing import Optional

from app.hashing import HashFunction, hash_pair, keccak256_hash
from app.proof import MerkleProof


@dataclass
class MerkleNode:
    """Represents a node in the Merkle Tree."""

    hash: bytes
    left: Optional["MerkleNode"] = None
    right: Optional["MerkleNode"] = None


class MerkleTree:
    """
    A binary Merkle Tree built from a list of hashes.
    Properly handles an odd number of leaves by duplicating the last node at each level.
    """

    def __init__(self, leaves: list[bytes], hash_fn: HashFunction = keccak256_hash):
        """
        Initialize the Merkle Tree.

        Args:
            leaves: A list of 32-byte hashes forming the leaves.
            hash_fn: The hashing function to use.
        """
        if not leaves:
            raise ValueError("Cannot construct a MerkleTree without leaves")

        self.hash_fn = hash_fn
        self.leaves = leaves.copy()

        # Build the lowest level nodes
        current_level = [MerkleNode(hash=leaf) for leaf in self.leaves]
        self.levels: list[list[MerkleNode]] = [current_level]

        self.root_node = self._build(current_level)

    def _build(self, nodes: list[MerkleNode]) -> MerkleNode:
        """
        Recursively build the tree from the bottom up.
        """
        if len(nodes) == 1:
            return nodes[0]

        next_level = []
        for i in range(0, len(nodes), 2):
            left_node = nodes[i]
            # Duplicate the last odd node if needed
            right_node = nodes[i + 1] if i + 1 < len(nodes) else left_node

            parent_hash = hash_pair(left_node.hash, right_node.hash, self.hash_fn)
            parent_node = MerkleNode(hash=parent_hash, left=left_node, right=right_node)
            next_level.append(parent_node)

        self.levels.append(next_level)
        return self._build(next_level)

    @property
    def root(self) -> bytes:
        """Returns the 32-byte root hash of the tree."""
        return self.root_node.hash

    def get_proof(self, index: int) -> MerkleProof:
        """
        Generate a Merkle proof for the leaf at the given index.

        Args:
            index: The 0-based index of the target leaf.

        Returns:
            A MerkleProof object containing the path of sibling hashes.
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds")

        target_hash = self.leaves[index]
        path = []

        # Walk up the tree to build the proof
        curr_idx = index
        for level in self.levels[:-1]:  # Exclude root level
            is_right_node = curr_idx % 2 == 1

            if is_right_node:
                sibling_idx = curr_idx - 1
                is_left_sibling = True
            else:
                sibling_idx = curr_idx + 1
                is_left_sibling = False

            # If sibling_idx is out of bounds, it means the current node was duplicated
            if sibling_idx >= len(level):
                sibling_idx = curr_idx

            sibling_hash = level[sibling_idx].hash
            path.append((sibling_hash, is_left_sibling))

            # Move to parent index
            curr_idx = curr_idx // 2

        return MerkleProof(target_hash=target_hash, target_index=index, path=path)

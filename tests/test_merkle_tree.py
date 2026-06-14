import pytest

from app.hashing import hash_pair, keccak256_hash
from app.merkle_tree import MerkleTree


def test_empty_tree():
    with pytest.raises(ValueError):
        MerkleTree([])


def test_single_leaf_tree():
    leaf = keccak256_hash(b"tx1")
    tree = MerkleTree([leaf])
    assert tree.root == leaf


def test_even_leaves_tree(mock_transactions):
    leaves = mock_transactions[:4]
    tree = MerkleTree(leaves)

    # Manual calculation
    hash01 = hash_pair(leaves[0], leaves[1])
    hash23 = hash_pair(leaves[2], leaves[3])
    expected_root = hash_pair(hash01, hash23)

    assert tree.root == expected_root


def test_odd_leaves_tree(mock_transactions):
    leaves = mock_transactions[:3]
    tree = MerkleTree(leaves)

    # Manual calculation
    hash01 = hash_pair(leaves[0], leaves[1])
    # The third leaf should be duplicated
    hash22 = hash_pair(leaves[2], leaves[2])
    expected_root = hash_pair(hash01, hash22)

    assert tree.root == expected_root

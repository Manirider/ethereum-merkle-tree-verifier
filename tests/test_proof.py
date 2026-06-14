import pytest

from app.merkle_tree import MerkleTree
from app.proof import verify_proof


@pytest.mark.parametrize("num_leaves", [1, 2, 3, 4, 5, 8])
def test_proof_generation_and_verification(num_leaves):
    from app.hashing import keccak256_hash

    leaves = [keccak256_hash(f"tx{i}".encode()) for i in range(num_leaves)]
    if num_leaves == 0:
        return

    tree = MerkleTree(leaves)

    for i in range(num_leaves):
        proof = tree.get_proof(i)
        assert proof.target_hash == leaves[i]
        assert proof.target_index == i
        assert verify_proof(proof, tree.root) is True


def test_invalid_proof_index(mock_transactions):
    tree = MerkleTree(mock_transactions[:3])
    with pytest.raises(IndexError):
        tree.get_proof(5)


def test_tampered_proof(mock_transactions):
    tree = MerkleTree(mock_transactions[:4])
    proof = tree.get_proof(1)

    # Tamper with target hash
    tampered_target = type(proof)(
        target_hash=b"wrong_hash" + b"0" * 22,
        target_index=proof.target_index,
        path=proof.path,
    )
    assert verify_proof(tampered_target, tree.root) is False

    # Tamper with path
    tampered_path_list = list(proof.path)
    tampered_path_list[0] = (b"wrong_hash" + b"0" * 22, tampered_path_list[0][1])
    tampered_path = type(proof)(
        target_hash=proof.target_hash,
        target_index=proof.target_index,
        path=tampered_path_list,
    )
    assert verify_proof(tampered_path, tree.root) is False


def test_proof_string_representation(mock_transactions):
    tree = MerkleTree(mock_transactions[:3])
    proof = tree.get_proof(1)
    proof_str = str(proof)
    assert "MerkleProof for leaf at index 1:" in proof_str
    assert "Target: " in proof_str


def test_verify_proof_empty_target_hash(mock_transactions):
    tree = MerkleTree(mock_transactions[:3])
    proof = tree.get_proof(1)
    # Create a proof with empty target_hash
    from app.proof import MerkleProof

    empty_proof = MerkleProof(
        target_hash=b"", target_index=proof.target_index, path=proof.path
    )
    assert verify_proof(empty_proof, tree.root) is False

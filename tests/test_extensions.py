import pytest

from app.extensions import (
    LightClientSimulator,
    rlp_encode,
    verify_historical_blocks,
    verify_odd_leaf_duplication,
)
from app.hashing import keccak256_hash
from app.merkle_tree import MerkleTree


def test_rlp_encode_bytes():
    # Single byte less than 0x80
    assert rlp_encode(b"\x0f") == b"\x0f"
    # Short bytes
    assert rlp_encode(b"dog") == b"\x83dog"
    # Long bytes (> 55 bytes)
    long_bytes = b"a" * 60
    encoded = rlp_encode(long_bytes)
    assert encoded[0] == 0xB7 + 1
    assert encoded[1] == 60
    assert encoded[2:] == long_bytes


def test_rlp_encode_string():
    assert rlp_encode("dog") == b"\x83dog"


def test_rlp_encode_list():
    assert rlp_encode(["cat", "dog"]) == b"\xc8\x83cat\x83dog"


def test_rlp_encode_invalid_type():
    with pytest.raises(TypeError):
        rlp_encode(123)  # type: ignore


def test_verify_odd_leaf_duplication():
    # Even leaf tree (no bottom duplication)
    leaves_even = [keccak256_hash(b"1"), keccak256_hash(b"2")]
    tree_even = MerkleTree(leaves_even)
    assert verify_odd_leaf_duplication(tree_even) is True

    # Odd leaf tree
    leaves_odd = [keccak256_hash(b"1"), keccak256_hash(b"2"), keccak256_hash(b"3")]
    tree_odd = MerkleTree(leaves_odd)
    assert verify_odd_leaf_duplication(tree_odd) is True


def test_light_client_simulator(mock_transactions):
    tree = MerkleTree(mock_transactions)
    client = LightClientSimulator()

    # Header ingestion
    client.ingest_block_header(100, tree.root)

    # Valid verification
    proof = tree.get_proof(2)
    assert client.verify_transaction(100, proof) is True

    # Non-ingested block error
    with pytest.raises(ValueError):
        client.verify_transaction(101, proof)


def test_verify_historical_blocks(mocker):
    # Mock fetch_block to return a valid simplified block format
    mock_block = {
        "number": "0x1b4",
        "timestamp": "0x55ba4224",
        "transactionsRoot": "0x" + "a" * 64,
        "transactions": [
            {"hash": "0x" + "b" * 64, "nonce": "0x1"},
            {"hash": "0x" + "c" * 64, "nonce": "0x2"},
        ],
    }
    mocker.patch("app.extensions.fetch_block", return_value=mock_block)

    res = verify_historical_blocks(436, 1)
    assert 436 in res
    assert res[436] is True


def test_rlp_encode_long_list():
    # List containing long items such that total RLP body > 55 bytes
    long_list = ["a" * 30, "b" * 30]
    encoded = rlp_encode(long_list)
    assert encoded[0] == 0xF7 + 1
    assert encoded[1] == 62  # length of body is (30 + 1 prefix) + (30 + 1 prefix) = 62
    # let's just make sure it encodes without errors and starts with the list long prefix prefix.
    assert encoded[0] == 0xF8


def test_verify_historical_blocks_empty(mocker):
    mock_block = {
        "number": "0x1b4",
        "timestamp": "0x55ba4224",
        "transactionsRoot": "0x" + "a" * 64,
        "transactions": [],
    }
    mocker.patch("app.extensions.fetch_block", return_value=mock_block)
    res = verify_historical_blocks(436, 1)
    assert res[436] is True


def test_verify_historical_blocks_exception(mocker):
    mocker.patch("app.extensions.fetch_block", side_effect=Exception("RPC Error"))
    res = verify_historical_blocks(436, 1)
    assert res[436] is False

import pytest

from app.hashing import keccak256_hash


@pytest.fixture
def mock_transactions():
    """Returns a list of mock 32-byte transaction hashes."""
    return [
        keccak256_hash(b"tx1"),
        keccak256_hash(b"tx2"),
        keccak256_hash(b"tx3"),
        keccak256_hash(b"tx4"),
        keccak256_hash(b"tx5"),
    ]


@pytest.fixture
def mock_block():
    """Returns a mock Ethereum block dictionary."""
    return {
        "number": "0x1b4",
        "timestamp": "0x55ba4224",
        "transactionsRoot": "0x" + "a" * 64,
        "transactions": [
            {"hash": "0x" + "b" * 64, "nonce": "0x1"},
            {"hash": "0x" + "c" * 64, "nonce": "0x2"},
        ],
    }

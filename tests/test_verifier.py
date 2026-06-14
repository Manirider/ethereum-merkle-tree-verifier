from app.utils import hex_to_bytes
from app.verifier import (
    hash_transaction_rlp,
    hash_transaction_simple,
    reconstruct_transactions_root,
    verify_transactions_root,
)


def test_hash_transaction_simple():
    tx = {"hash": "0xabc", "nonce": "0x1"}
    h = hash_transaction_simple(tx)
    assert len(h) == 32


def test_hash_transaction_rlp():
    tx = {"hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"}
    h = hash_transaction_rlp(tx)
    assert len(h) == 32
    assert h == hex_to_bytes(tx["hash"])


def test_reconstruct_empty_transactions():
    root, tree = reconstruct_transactions_root([], hash_mode="real")
    assert (
        root.hex() == "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
    )
    assert tree is None


def test_hash_transaction_rlp_missing_hash():
    import pytest

    with pytest.raises(ValueError, match="Transaction object missing 'hash' field"):
        hash_transaction_rlp({"nonce": "0x1"})


def test_reconstruct_transactions_root_real():
    txs = [{"hash": "0x" + "1" * 64}, {"hash": "0x" + "2" * 64}]
    root, tree = reconstruct_transactions_root(txs, hash_mode="real")
    assert root is not None
    assert tree is not None
    assert len(tree.leaves) == 2


def test_reconstruct_transactions_root_simple():
    txs = [
        {"hash": "0x" + "1" * 64, "nonce": "0x1"},
        {"hash": "0x" + "2" * 64, "nonce": "0x2"},
    ]
    root, tree = reconstruct_transactions_root(txs, hash_mode="simple")
    assert root is not None
    assert tree is not None
    assert len(tree.leaves) == 2


def test_verify_transactions_root(mock_block):
    # Match case
    # Since mock_block transactions have hashes "0x" + "b"*64 and "0x" + "c"*64,
    # let's compute the expected root and set it
    txs = mock_block["transactions"]
    root, _ = reconstruct_transactions_root(txs, hash_mode="real")
    mock_block["transactionsRoot"] = "0x" + root.hex()

    assert verify_transactions_root(mock_block, hash_mode="real") is True

    # Mismatch case
    mock_block["transactionsRoot"] = "0x" + "d" * 64
    assert verify_transactions_root(mock_block, hash_mode="real") is False
    assert verify_transactions_root(mock_block, hash_mode="simple") is False

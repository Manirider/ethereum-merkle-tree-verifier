from app.ethereum import fetch_block, inspect_block
from app.proof import verify_proof
from app.utils import bytes_to_hex
from app.verifier import reconstruct_transactions_root, verify_transactions_root


def run_demo() -> None:
    print("=== Part 3: Full Ethereum Transactions Verification ===")

    # Fetch block
    block_num = 15000000
    try:
        block = fetch_block(block_num)
    except Exception as e:
        print(f"Failed to fetch block: {e}")
        return

    inspect_block(block)

    print("\n--- Verifying Transactions Root ---")
    verify_transactions_root(block, hash_mode="real")

    print("\n--- Testing Proof of Inclusion ---")
    transactions = block.get("transactions", [])
    if not transactions:
        print("No transactions in block to prove.")
        return

    _, tree = reconstruct_transactions_root(transactions, hash_mode="real")

    # Select a transaction near the middle
    target_idx = len(transactions) // 2
    target_tx = transactions[target_idx]

    print(f"Selected Transaction at index {target_idx}:")
    print(f"  Hash: {target_tx['hash']}")

    proof = tree.get_proof(target_idx)
    print("\nGenerated Proof Path:")
    for i, (sibling, is_left) in enumerate(proof.path):
        side = "LEFT " if is_left else "RIGHT"
        print(f"  Step {i}: {side} -> {bytes_to_hex(sibling)}")

    is_valid = verify_proof(proof, tree.root)
    print(f"\nProof verification result: {'SUCCESS' if is_valid else 'FAILED'}")

    # Tampering test
    print("\n--- Tampering with Proof ---")
    tampered_path = list(proof.path)
    if tampered_path:
        # Flip first byte of the first sibling hash
        bad_hash = bytearray(tampered_path[0][0])
        bad_hash[0] ^= 0xFF
        tampered_path[0] = (bytes(bad_hash), tampered_path[0][1])

    tampered_proof = type(proof)(
        target_hash=proof.target_hash,
        target_index=proof.target_index,
        path=tampered_path,
    )

    is_tampered_valid = verify_proof(tampered_proof, tree.root)
    print(
        f"Tampered proof verification result: {'SUCCESS (Wait, what?)' if is_tampered_valid else 'FAILED (As expected)'}"
    )


if __name__ == "__main__":
    run_demo()

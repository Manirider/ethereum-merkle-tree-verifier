from app.hashing import sha256_hash
from app.merkle_tree import MerkleTree
from app.proof import verify_proof
from app.utils import bytes_to_hex


def run_demo() -> None:
    print("=== Part 1: Basic Merkle Tree Construction ===")

    # 1. Create some dummy transaction data
    tx_data = [b"tx1", b"tx2", b"tx3", b"tx4", b"tx5"]
    leaves = [sha256_hash(tx) for tx in tx_data]

    print(
        f"Creating Merkle tree with {len(leaves)} leaves (odd number demonstrates duplication)."
    )

    # 2. Build tree
    tree = MerkleTree(leaves, hash_fn=sha256_hash)
    print(f"Computed Root: {bytes_to_hex(tree.root)}")

    # 3. Generate a proof for the middle transaction
    index = 2
    print(
        f"\nGenerating proof for leaf index {index} (Data: '{tx_data[index].decode()}')"
    )
    proof = tree.get_proof(index)
    print(proof)

    # 4. Verify proof
    is_valid = verify_proof(proof, tree.root, hash_fn=sha256_hash)
    print(f"Proof valid? {is_valid}")

    # 5. Tamper with proof to demonstrate failure
    print("\nTampering with proof (flipping a bit in the target hash)...")
    tampered_hash = bytearray(proof.target_hash)
    tampered_hash[0] ^= 0xFF

    tampered_proof = type(proof)(
        target_hash=bytes(tampered_hash),
        target_index=proof.target_index,
        path=proof.path,
    )
    is_valid_tampered = verify_proof(tampered_proof, tree.root, hash_fn=sha256_hash)
    print(f"Tampered proof valid? {is_valid_tampered}")


if __name__ == "__main__":
    run_demo()

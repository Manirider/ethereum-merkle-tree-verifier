from app.ethereum import fetch_block, inspect_block


def run_demo() -> None:
    print("=== Part 2: Fetching Ethereum Block ===")

    # Let's fetch a known block, e.g., block 15000000
    block_num = 15000000
    print(f"Attempting to fetch block {block_num} from RPC node...")

    try:
        block = fetch_block(block_num)
        inspect_block(block)
    except Exception as e:
        print(f"Error fetching block: {e}")


if __name__ == "__main__":
    run_demo()

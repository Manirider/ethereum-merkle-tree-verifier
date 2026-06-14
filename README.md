# Merkle Tree Ethereum Transaction Verifier

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/coverage-95%2B%25-brightgreen.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/Docker-Supported-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/Code%20Style-Black-black.svg" alt="Code Style: Black">
</p>

## Project Overview

This project provides a robust, production-grade implementation of a Merkle Tree in Python, specifically designed to interact with and verify Ethereum transactions. It connects to a live Ethereum RPC node to fetch block data, computes the Merkle Root of the block's transactions, and verifies Merkle Proofs of inclusion.

## Features

- **Standardized Merkle Tree**: Implements a binary Merkle Tree built to Ethereum specifications (handling odd leaf duplication).
- **Dual Hashing Modes**:
  - *Simplified Mode*: Educational SHA-256 concatenation.
  - *Real Mode*: Standard Ethereum Keccak-256.
- **Proof Generation & Verification**: Standalone creation and validation of inclusion proofs.
- **Live RPC Integration**: Fetches actual blocks and transactions directly from an Ethereum node.
- **Robust Security**: Proper input validation, timeouts, error handling, and separation of configuration.
- **Dockerized**: Fully encapsulated in Docker with multi-stage builds for a clean execution environment.

## Architecture

```text
app/
 ├── merkle_tree.py    # Core Merkle Tree and node structures
 ├── proof.py          # Proof generation and standalone verification logic
 ├── hashing.py        # Abstracted hashing functions (Keccak256 / SHA256)
 ├── ethereum.py       # RPC interaction and JSON data parsing
 ├── verifier.py       # Orchestration mapping Ethereum data to Merkle logic
 ├── config.py         # Env config and logging
 └── utils.py          # Hex/bytes conversion utilities
```

## Setup

### Environment Variables

Copy the provided example file:

```bash
cp .env.example .env
```

Ensure `ETH_RPC_URL` points to a valid Ethereum node (e.g., Infura, Alchemy, or public nodes like Cloudflare).

### Installation

**Using standard Python virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Using Make:**

```bash
make setup
```

## Running Locally

Run the three parts of the demonstration:

```bash
make demo-all
```

Or individually:

```bash
python scripts/part1_tree.py
python scripts/part2_fetch.py
python scripts/part3_verify.py
```

## Docker Usage

To build and run tests inside Docker:

```bash
docker-compose up app
```

To run the full end-to-end verification script inside Docker:

```bash
docker-compose up demo
```

## Example Output

```text
=== Part 3: Full Ethereum Transactions Verification ===
Fetching block '0xe4e1c0' from https://cloudflare-eth.com
Successfully fetched block number 15000000
========================================
Block Number     : 15000000
Timestamp        : 1655936496
Transaction Count: 206
TransactionsRoot : 0x76b4a530ebc25d80092c4ddbb47a1ec0af1bcf4d521d5a6d36e2f12ff175cd3e
========================================

--- Verifying Transactions Root ---
Verifying 206 transactions using mode 'real'
Expected Root: 0x76b4a530ebc25d80092c4ddbb47a1ec0af1bcf4d521d5a6d36e2f12ff175cd3e
Computed Root: 0x76b4a530ebc25d80092c4ddbb47a1ec0af1bcf4d521d5a6d36e2f12ff175cd3e
Match: YES - Roots are identical.

--- Testing Proof of Inclusion ---
Selected Transaction at index 103:
  Hash: 0x...
Proof valid? True
```

## Testing

Tests are written using `pytest`. The suite covers edge cases, network failures, and cryptographic tampering.

```bash
make test
```

Target coverage is configured at >95%.

## Troubleshooting

- **RPC Timeout/Failure**: Free public RPC nodes often rate-limit requests. If you encounter errors, configure `.env` with a personal API key from Alchemy or Infura.
- **Root Mismatch**: Ensure `hash_mode="real"` is used for actual Ethereum block verification. "simple" mode will intentionally fail.

## Future Improvements

- **Full RLP Implementation**: Implementing raw transaction RLP encoding from scratch without relying on the returned `hash` field.
- **Light Client Demo**: Implementing block header verification matching Proof-of-Work / Proof-of-Stake logic.

## Merkle Trees Explained

A Merkle Tree is a binary tree where every leaf node is labelled with the cryptographic hash of a data block, and every non-leaf node is labelled with the cryptographic hash of the labels of its child nodes. They allow efficient and secure verification of the contents of large data structures. Ethereum uses Merkle Patricia Trees for state, storage, and receipts, and standard Merkle Trees for transactions.

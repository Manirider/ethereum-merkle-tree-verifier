from typing import Any

import requests

from app.config import ETH_RPC_URL, setup_logger

logger = setup_logger(__name__)


class EthereumRPCError(Exception):
    pass


def fetch_block(
    block_identifier: str | int, retries: int = 3, timeout: int = 10
) -> dict[str, Any]:
    """
    Fetch a full block with transaction objects from an Ethereum JSON-RPC endpoint.

    Args:
        block_identifier: Block number (int or hex string) or 'latest'.
        retries: Number of retry attempts.
        timeout: Request timeout in seconds.

    Returns:
        The block dictionary containing transaction objects.
    """
    if isinstance(block_identifier, int):
        block_param = hex(block_identifier)
    else:
        block_param = block_identifier

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_param, True],  # True to fetch full transaction objects
        "id": 1,
    }

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                f"Fetching block '{block_param}' from {ETH_RPC_URL} (attempt {attempt}/{retries})"
            )
            response = requests.post(ETH_RPC_URL, json=payload, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            if "error" in data:
                raise EthereumRPCError(
                    f"RPC Error: {data['error'].get('message', data['error'])}"
                )

            block = data.get("result")
            if not block:
                raise EthereumRPCError("Block not found or null result.")
            if not isinstance(block, dict):
                raise EthereumRPCError("Expected block result to be a dictionary.")

            logger.info(f"Successfully fetched block number {int(block['number'], 16)}")
            return block

        except (requests.RequestException, EthereumRPCError) as e:
            logger.warning(
                f"Failed to fetch block (attempt {attempt}/{retries}): {e!s}"
            )
            if attempt == retries:
                logger.error("Max retries reached. Could not fetch block.")
                raise

    raise EthereumRPCError("Unreachable")


def inspect_block(block: dict[str, Any]) -> None:
    """Print key details of an Ethereum block."""
    try:
        block_num = int(block["number"], 16)
        tx_count = len(block["transactions"])
        timestamp = int(block["timestamp"], 16)
        tx_root = block["transactionsRoot"]

        print("=" * 40)
        print(f"Block Number     : {block_num}")
        print(f"Timestamp        : {timestamp}")
        print(f"Transaction Count: {tx_count}")
        print(f"TransactionsRoot : {tx_root}")
        print("=" * 40)
    except KeyError as e:
        logger.error(f"Malformed block object, missing key: {e}")

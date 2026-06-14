import pytest
import requests

from app.ethereum import EthereumRPCError, fetch_block


def test_fetch_block_success(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": {"number": "0x1b4"}}
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.post", return_value=mock_response)

    block = fetch_block(436)
    assert block["number"] == "0x1b4"


def test_fetch_block_rpc_error(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"error": {"message": "Invalid block"}}
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.post", return_value=mock_response)

    with pytest.raises(EthereumRPCError, match="Invalid block"):
        fetch_block("invalid")


def test_fetch_block_network_error(mocker):
    mocker.patch("requests.post", side_effect=requests.RequestException("Timeout"))

    with pytest.raises(requests.RequestException):
        fetch_block(436, retries=1)


def test_fetch_block_null_result(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": None}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.post", return_value=mock_response)

    with pytest.raises(EthereumRPCError, match="Block not found or null result"):
        fetch_block(436, retries=1)


def test_fetch_block_hex_identifier(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": {"number": "0x1b4"}}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.post", return_value=mock_response)

    block = fetch_block("0x1b4")
    assert block["number"] == "0x1b4"


def test_inspect_block_success(capsys):
    from app.ethereum import inspect_block

    block = {
        "number": "0xe4e1c0",
        "timestamp": "0x62b3a8d0",
        "transactionsRoot": "0x76b4a530ebc25d80092c4ddbb47a1ec0af1bcf4d521d5a6d36e2f12ff175cd3e",
        "transactions": [1, 2, 3],
    }
    inspect_block(block)
    captured = capsys.readouterr()
    assert "Block Number     : 15000000" in captured.out
    assert "Timestamp        : 1655941328" in captured.out
    assert "Transaction Count: 3" in captured.out


def test_inspect_block_malformed(capsys):
    from app.ethereum import inspect_block

    # Missing transactions key
    block = {
        "number": "0xe4e1c0",
        "timestamp": "0x62b3a8d0",
        "transactionsRoot": "0x76b4a530ebc25d80092c4ddbb47a1ec0af1bcf4d521d5a6d36e2f12ff175cd3e",
    }
    inspect_block(block)
    # It should log error, not crash
    captured = capsys.readouterr()
    assert captured.out == ""

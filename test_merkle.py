import pytest
import json

from merkle import mtr

def do_test_fixture(fixture_path):
    with open(fixture_path, 'r') as f:
        fixture = json.load(f)
    expected_merkleroot = bytes.fromhex(fixture['merkleroot'])[::-1]
    txs = [bytes.fromhex(tx_id)[::-1] for tx_id in fixture['txs']]
    assert mtr(txs) == expected_merkleroot

def test_bitcoin_block_100():
    do_test_fixture('./fixtures/merkle/bitcoin_block_100.json')

def test_bitcoin_cash_testnet_2_txs():
    do_test_fixture('./fixtures/merkle/bitcoin_cash_testnet_2_txs.json')

def test_bitcoin_cash_testnet_big():
    do_test_fixture('./fixtures/merkle/bitcoin_cash_testnet_1259110.json')

def test_no_leafs():
    with pytest.raises(AssertionError):
        mtr([])

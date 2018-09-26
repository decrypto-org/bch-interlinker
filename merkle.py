def mtr(leafs):
    assert len(leafs) > 0

    from hashlib import sha256
    from itertools import zip_longest

    def hash_siblings(l, r):
        h1, h2 = sha256(), sha256()
        h1.update(l)
        h1.update(r)
        h2.update(h1.digest())
        return h2.digest()

    def next_level(level):
        return [hash_siblings(l, r) for l, r in zip_longest(level[::2], level[1::2], fillvalue=level[-1])]

    level = leafs
    while len(level) > 1:
        level = next_level(level)
    return level[0]

if __name__ == '__main__':
    import unittest
    import json

    class MerkleTest(unittest.TestCase):
        def do_test_fixture(self, fixture_path):
            with open(fixture_path, 'r') as f:
                fixture = json.load(f)
            expected_merkleroot = bytes.fromhex(fixture['merkleroot'])[::-1]
            txs = [bytes.fromhex(tx_id)[::-1] for tx_id in fixture['txs']]
            self.assertEqual(mtr(txs), expected_merkleroot)

        def test_bitcoin_block_100(self):
            self.do_test_fixture('./fixtures/merkle/bitcoin_block_100.json')

        def test_bitcoin_cash_testnet_2_txs(self):
            self.do_test_fixture('./fixtures/merkle/bitcoin_cash_testnet_2_txs.json')

        def test_bitcoin_cash_testnet_big(self):
            self.do_test_fixture('./fixtures/merkle/bitcoin_cash_testnet_1259110.json')

        def test_no_leafs(self):
            with self.assertRaises(AssertionError):
                mtr([])


    unittest.main()

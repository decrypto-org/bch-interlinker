def mtr(leafs):
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

    class MerkleTest(unittest.TestCase):
        def test_bitcoin_block_100(self):
            expected_merkleroot = bytes.fromhex("f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766")[::-1]
            txs = [
                    bytes.fromhex(tx_id)[::-1] for tx_id in [
                        "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
                        "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
                        "6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
                        "e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
                        ]
                    ]
            self.assertEqual(mtr(txs), expected_merkleroot)

        def test_bitcoin_cash_testnet(self):
            expected_merkleroot = bytes.fromhex("5e6373969c5709934527e68e828f8ee406cabf9c3b3aab245120f9ae02107979")[::-1]
            txs = [
                    bytes.fromhex(tx_id)[::-1] for tx_id in [
                        "08187470ec1230d4e95f295aa11eb6f73c124b0f21e1c81e465f914b463a1290",
                        "32b89239177f382f0b003ba71193e9754b3c0709e7d3f2fce597029b4784c30d"
                        ]
                    ]
            self.assertEqual(mtr(txs), expected_merkleroot)


    unittest.main()

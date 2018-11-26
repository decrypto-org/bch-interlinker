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

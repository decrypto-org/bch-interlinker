from interlink import Interlink

def test_interlink():
    interlink = Interlink(genesis=b'\x01')
    interlink = interlink.update('0c', 5)
    interlink = interlink.update('0b', 4)
    interlink = interlink.update('0a', 2)
    assert interlink.as_array() == [b'\x0a', b'\x0a', b'\x0a', b'\x0b', b'\x0b', b'\x0c', b'\x01']

def test_interlink_cascading():
    interlink = Interlink(genesis=b'\x02')
    interlink = interlink.update('0a', 2)
    interlink = interlink.update('0b', 4)
    interlink = interlink.update('0c', 5)
    assert interlink.as_array() == [b'\x0c'] * 6 + [b'\x02']

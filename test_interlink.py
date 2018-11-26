from interlink import Interlink

def test_interlink():
    interlink = Interlink()
    interlink = interlink.update('z', 5)
    interlink = interlink.update('y', 4)
    interlink = interlink.update('x', 2)
    assert interlink.as_array() == ['x', 'x', 'x', 'y', 'y', 'z']

def test_interlink_cascading():
    interlink = Interlink()
    interlink = interlink.update('x', 2)
    interlink = interlink.update('y', 4)
    interlink = interlink.update('z', 5)
    assert interlink.as_array() == ['z'] * 6

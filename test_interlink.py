from interlink import Interlink

def test_interlink():
    interlink = Interlink()
    interlink.update('z', 5)
    interlink.update('y', 4)
    interlink.update('x', 2)
    assert interlink.as_array() == ['x', 'x', 'x', 'y', 'y', 'z']

def test_interlink_cascading():
    interlink = Interlink()
    interlink.update('x', 2)
    interlink.update('y', 4)
    interlink.update('z', 5)
    assert interlink.as_array() == ['z'] * 6

import pytest

from helpers import compact_list_repr

def test_compact_list_repr():
    assert compact_list_repr(['a', 'a', 'b', 'b', 'b', 'c', 'c']) == '[2 * a, 3 * b, 2 * c]'
    assert compact_list_repr([]) == '[]'

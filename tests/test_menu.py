
import pytest

from src.menu import Menu

# In memory client for unit/integration tests
@pytest.fixture()
def menu():
    menu = Menu()
    return menu

def test_init():
    menu = Menu()
    assert(menu._title == "")
    assert(bool(menu._options) == False)
    assert(bool(menu._option_map) == False)
    assert(bool(menu._func_map) == False)
    assert(menu._num_options == 0)
    assert(menu._border_char == "*")
    assert(menu._width == 0)
    assert(menu._height == 0)
    assert(menu._width_mod == 12)

def test_set_title(menu):
    menu.set_title("TEST TITLE")
    assert(menu._title == "TEST TITLE")
    
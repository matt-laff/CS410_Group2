
import pytest

from src.menu import Menu

# In memory client for unit/integration tests
@pytest.fixture()
def menu():
    menu = Menu()
    return menu

@pytest.fixture()
def opt_menu():
    opt_menu = Menu()
    opt_menu.add_option("opt1", option_func)
    return opt_menu


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

def test_add_option(menu):
    menu.add_option("opt1", option_func) 
    assert(menu._num_options == 1)
    assert(menu._options[0] == "opt1")
    assert(menu._option_map[1] == "opt1")
    assert(menu._height == 1)

    menu.add_option("no_func_opt", None)
    assert(menu._num_options == 2)
    assert(menu._options[1] == "no_func_opt")
    assert(menu._option_map[2] == "no_func_opt")
    assert(menu._height == 2)
    assert(menu._func_map["no_func_opt"] == None)

def test_execute_option(opt_menu):
    assert(opt_menu._func_map["opt1"]() == True)

def option_func():
    return True
    
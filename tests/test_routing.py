import pytest
import byrdie.routing
from byrdie.routing import route, Router

# Fixture to reset the global router before each test
@pytest.fixture(autouse=True)
def reset_router():
    # We need to replace the global router instance in the routing module
    # with a fresh one for each test to ensure isolation.
    new_router = Router()
    # Keep a reference to the original router to restore it later
    original_router = byrdie.routing.router
    byrdie.routing.router = new_router
    yield
    # Restore the original router after the test has run
    byrdie.routing.router = original_router


def test_explicit_path():
    @route("/explicit/path")
    def my_view():
        pass

    assert byrdie.routing.router.get_view("/explicit/path") == my_view
    assert my_view.route_path == "/explicit/path"

def test_implicit_path_with_parentheses():
    @route()
    def my__implicit__view():
        pass

    assert byrdie.routing.router.get_view("/my/implicit/view") == my__implicit__view
    assert my__implicit__view.route_path == "/my/implicit/view"

def test_implicit_path_no_parentheses():
    @route
    def another__implicit__view():
        pass

    assert byrdie.routing.router.get_view("/another/implicit/view") == another__implicit__view
    assert another__implicit__view.route_path == "/another/implicit/view"

def test_duplicate_route_raises_error():
    @route("/duplicate")
    def view1():
        pass

    with pytest.raises(ValueError, match="Route for path '/duplicate' is already registered."):
        @route("/duplicate")
        def view2():
            pass

def test_root_path():
    @route("/")
    def root_view():
        pass

    assert byrdie.routing.router.get_view("/") == root_view
    assert root_view.route_path == "/"

def test_path_with_trailing_slash_in_name():
    # Functions with trailing dunders should not result in trailing slashes in the URL
    @route
    def trailing__slash__():
        pass

    assert byrdie.routing.router.get_view("/trailing/slash") == trailing__slash__
    assert trailing__slash__.route_path == "/trailing/slash"

def test_get_nonexistent_view():
    assert byrdie.routing.router.get_view("/nonexistent") is None

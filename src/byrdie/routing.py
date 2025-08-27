import inspect
from typing import Callable, Dict, Optional

class Router:
    def __init__(self):
        self.routes: Dict[str, Callable] = {}

    def register(self, path: str, view: Callable):
        if path in self.routes:
            raise ValueError(f"Route for path '{path}' is already registered.")
        self.routes[path] = view

    def get_view(self, path: str) -> Optional[Callable]:
        return self.routes.get(path)

# Global router instance
router = Router()

def route(path: Optional[str] = None, **kwargs) -> Callable:
    # This case handles when @route is used without parentheses
    if callable(path):
        view = path
        # Generate implicit path
        new_path = "/" + view.__name__.replace("__", "/").strip("/")
        router.register(new_path, view)
        view.route_path = new_path
        return view

    # This case handles when @route is used with parentheses, e.g., @route("/my-path")
    def decorator(view: Callable) -> Callable:
        # Use the path from the outer scope
        route_path = path
        if route_path is None:
            route_path = "/" + view.__name__.replace("__", "/").strip("/")

        if kwargs.get("api"):
            route_path = "/api" + route_path

        router.register(route_path, view)
        # Attach path to the view for easier testing
        view.route_path = route_path
        view.is_authenticated = kwargs.get("is_authenticated", False)
        view.has_permissions = kwargs.get("has_permissions", None)

        # Inspect the view to find the response schema
        sig = inspect.signature(view)
        return_annotation = sig.return_annotation
        if return_annotation is not inspect.Signature.empty:
            view.response_schema = return_annotation
        else:
            view.response_schema = None

        return view
    return decorator

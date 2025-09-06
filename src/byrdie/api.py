import inspect
from functools import wraps
from typing import Callable, Dict, Optional, List, get_origin, get_args

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import engines
from django.template.loader import get_template, TemplateDoesNotExist
from django.urls import path as url_path

from .schemas import BaseModel, ModelSchema


class Router:
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.views: Dict[Callable, str] = {}

    def register(self, path: str, view: Callable, is_provisional: bool = False):
        if path in self.routes and not is_provisional:
            raise ValueError(f"Route for path '{path}' is already registered.")

        self.routes[path] = view
        self.views[view] = path

    def get_view(self, path: str) -> Optional[Callable]:
        return self.routes.get(path)


class Api:
    def __init__(self):
        self.router = Router()

    @property
    def urls(self):
        """
        Returns a list of URL patterns for the registered routes.
        """
        urlpatterns = []
        for path_str, view in self.router.routes.items():
            # Django paths should not start with a slash
            if path_str.startswith('/'):
                path_str = path_str[1:]
            urlpatterns.append(url_path(path_str, view))
        return urlpatterns

    def route(self, path: Optional[str] = None, **kwargs) -> Callable:
        if callable(path):
            view = path
            final_path = "/" + view.__name__.replace("__", "/").strip("/")
            wrapped_view = self._create_view_wrapper(view, **kwargs)
            self.router.register(final_path, wrapped_view)
            return wrapped_view

        def decorator(view: Callable) -> Callable:
            final_path = path
            if final_path is None:
                final_path = "/" + view.__name__.replace("__", "/").strip("/")

            if kwargs.get("api"):
                final_path = "/api" + final_path

            wrapped_view = self._create_view_wrapper(view, **kwargs)
            self.router.register(final_path, wrapped_view)
            return wrapped_view
        return decorator

    def add_schema(self, schema_cls):
        """
        Registers a schema and its routes.
        """
        schema_name = schema_cls.__name__.lower().replace('schema', '')

        for attr_name, attr_value in schema_cls.__dict__.items():

            is_classmethod = isinstance(attr_value, classmethod)
            view_func = attr_value.__func__ if is_classmethod else attr_value

            if not hasattr(view_func, 'is_action'):
                continue

            action_info = view_func.action_info

            # Build path
            path_template = action_info['path']
            if is_classmethod:
                path = path_template if path_template is not None else f"/{attr_name}"
            else: # instance method
                if path_template:
                    if '{pk}' not in path_template and '<int:pk>' not in path_template:
                        path = f"/<int:pk>{path_template}"
                    else:
                        path = path_template.replace("{pk}", "<int:pk>")
                else:
                    path = f"/<int:pk>/{attr_name}"

            full_path = f"/{schema_name}{path}"

            # Wrap and register
            wrapped_view = self._create_schema_view_wrapper(view_func, schema_cls, is_classmethod, **action_info['kwargs'])
            self.router.register(full_path, wrapped_view)

    def _create_view_wrapper(self, view: Callable, **kwargs) -> Callable:
        view.is_authenticated = kwargs.get("is_authenticated", False)
        view.has_permissions = kwargs.get("has_permissions", None)

        @wraps(view)
        def wrapper(request, *args, **route_kwargs):
            result = view(request, *args, **route_kwargs)

            sig = inspect.signature(view)
            return_annotation = sig.return_annotation
            response_schema = return_annotation if return_annotation is not inspect.Signature.empty else None

            if response_schema is None:
                if hasattr(result, '_default_schema'):
                    response_schema = result._default_schema
                elif isinstance(result, list) and result and hasattr(result[0], '_default_schema'):
                    response_schema = List[result[0]._default_schema]

            return self._process_view_result(result, response_schema, view)
        return wrapper

    def _create_schema_view_wrapper(self, view_func: Callable, schema_cls: type, is_classmethod: bool, **kwargs) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **route_kwargs):
            wrapper.is_authenticated = kwargs.get("is_authenticated", False)
            wrapper.has_permissions = kwargs.get("has_permissions", None)

            if is_classmethod:
                result = view_func(schema_cls, request, *args, **route_kwargs)
            else:
                pk = route_kwargs.get('pk')
                if not pk:
                    raise ValueError("Instance method route requires a 'pk' parameter in the URL.")

                model = getattr(schema_cls.Meta, 'model', None)
                if not model:
                    raise TypeError("ModelSchema used for an instance route must have a model defined in its Meta.")

                instance = get_object_or_404(model, pk=pk)
                schema_instance = schema_cls.model_validate(instance)
                result = view_func(schema_instance, request, *args, **route_kwargs)

            sig = inspect.signature(view_func)
            return_annotation = sig.return_annotation
            response_schema = return_annotation if return_annotation is not inspect.Signature.empty else None

            if response_schema is None:
                if hasattr(result, '_default_schema'):
                    response_schema = result._default_schema
                elif isinstance(result, list) and result and hasattr(result[0], '_default_schema'):
                    response_schema = List[result[0]._default_schema]

            return self._process_view_result(result, response_schema, view_func)
        return wrapper

    def _process_view_result(self, result: any, schema: any, view_func: Callable) -> HttpResponse:
        if isinstance(result, HttpResponse):
            return result

        # If the view returns a dictionary, we assume it's a context for a template.
        if isinstance(result, dict) and schema is None:
            template_name = f"{view_func.__name__}.html"
            try:
                template = get_template(template_name)
                # Check if the template extends a base template
                with open(template.origin.name) as f:
                    content = f.read()
                if not content.strip().startswith("{% extends"):
                    # If not, wrap it in the base template
                    content = '{% extends "base.html" %}{% block content %}' + content + '{% endblock %}'
                    template = engines['django'].from_string(content)

                return HttpResponse(template.render(result))

            except TemplateDoesNotExist:
                return HttpResponse(f"Template '{template_name}' not found for view '{view_func.__name__}'.", status=404)

        if schema is None:
            return HttpResponse(result)

        origin = get_origin(schema)
        if origin is list or origin is List:
            args = get_args(schema)
            if args and inspect.isclass(args[0]) and issubclass(args[0], BaseModel):
                validated_data = [args[0].model_validate(item).model_dump() for item in result]
                return JsonResponse(validated_data, safe=False)

        if inspect.isclass(schema) and issubclass(schema, BaseModel):
            validated_data = schema.model_validate(result).model_dump()
            return JsonResponse(validated_data)

        return HttpResponse(result)

def action(path: Optional[str] = None, **kwargs) -> Callable:
    def decorator(view: Callable) -> Callable:
        view.is_action = True
        view.action_info = {'path': path, 'kwargs': kwargs}
        return view
    return decorator

# Default API instance
api = Api()
route = api.route

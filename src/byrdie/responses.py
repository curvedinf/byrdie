"""
This module contains functions for processing view results and generating
appropriate Django HTTP responses, including JSON serialization for
Pydantic models.
"""
import inspect
from typing import get_origin, get_args
from django.http import HttpResponse, JsonResponse
from pydantic import BaseModel


def process_view_result(result: any, schema: any) -> HttpResponse:
    """
    Processes the result of a view function and returns an appropriate
    Django HTTP response.

    If the view's response schema is a Pydantic model, the result is
    serialized to JSON. Otherwise, a standard HttpResponse is returned.
    """
    if schema is None:
        return HttpResponse(result)

    origin = get_origin(schema)
    if origin is list:
        # Handle list[MySchema]
        args = get_args(schema)
        if args and inspect.isclass(args[0]) and issubclass(args[0], BaseModel):
            data = [item.model_dump() for item in result]
            return JsonResponse(data, safe=False)

    if inspect.isclass(schema) and issubclass(schema, BaseModel):
        # Handle MySchema
        return JsonResponse(result.model_dump())

    # Default case for other types
    return HttpResponse(result)


from functools import wraps

def create_view_wrapper(view):
    """
    Creates a wrapper around a view function that handles response serialization.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        # Call the original view to get the data
        result = view(request, *args, **kwargs)

        # Get the response schema from the original view
        schema = getattr(view, 'response_schema', None)

        # Process the result and return the response
        return process_view_result(result, schema)

    return wrapper

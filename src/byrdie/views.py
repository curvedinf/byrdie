import json
from django.apps import apps
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden

def call_exposed_method(request, app_label, model_name, pk, method_name):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST requests are allowed.")

    try:
        model_class = apps.get_model(app_label, model_name)
    except LookupError:
        return HttpResponseNotFound(f"Model {app_label}.{model_name} not found.")

    try:
        instance = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        return HttpResponseNotFound(f"Instance with pk {pk} not found.")

    if not hasattr(instance, method_name):
        return HttpResponseNotFound(f"Method {method_name} not found on model {model_name}.")

    method = getattr(instance, method_name)

    if not callable(method) or not hasattr(method, '_byrdie_exposed'):
        return HttpResponseForbidden(f"Method {method_name} is not exposed.")

    try:
        kwargs = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON in request body.")

    try:
        result = method(**kwargs)
    except Exception as e:
        # It's good practice to log the exception here.
        return HttpResponseBadRequest(f"Error calling method {method_name}: {e}")

    return JsonResponse(result)

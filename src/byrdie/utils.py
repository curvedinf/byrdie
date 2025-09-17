import ast
import inspect
import sys
import datetime
from django.apps import apps

# A mapping from Django field types to Python types for Pydantic
FIELD_TYPE_MAPPING = {
    'AutoField': int,
    'BigAutoField': int,
    'CharField': str,
    'IntegerField': int,
    'PositiveIntegerField': int,
    'FloatField': float,
    'BooleanField': bool,
    'DateField': datetime.date,
    'DateTimeField': datetime.datetime,
    'EmailField': str,
    'URLField': str,
    'TextField': str,
    'ForeignKey': int,  # By default, we'll expose the foreign key ID
    'OneToOneField': int,
}

def parse_imports(app_path):
    """
    Parse the app.py file to extract project-specific import module names.
    """
    with open(app_path, 'r') as f:
        tree = ast.parse(f.read(), filename=app_path)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                imports.add(module)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    # Filter out standard library, django, and byrdie
    stdlib_modules = set(sys.stdlib_module_names)
    project_imports = []
    for mod in imports:
        if mod in stdlib_modules:
            continue
        if mod.startswith('django.') or mod.startswith('byrdie.'):
            continue
        # For relative imports, the module name is already resolved without dots
        # Prefix with package name if needed, but assuming flat structure
        project_imports.append(mod)
    return list(set(project_imports))  # Ensure unique

def find_model_subclasses(modules):
    """
    Find all subclasses of byrdie.models.Model in the given modules.
    """
    from byrdie.models import Model
    subclasses = []
    for module in modules:
        members = inspect.getmembers(module, inspect.isclass)
        for name, cls in members:
            if issubclass(cls, Model) and cls is not Model:
                subclasses.append(cls)
    return subclasses

def register_discovered_models(model_classes, app_config):
    """
    Register discovered model classes with Django's app registry.
    """
    for model in model_classes:
        if not model._meta.app_label:
            model._meta.app_label = 'app'
        apps.register_model(app_config, model)

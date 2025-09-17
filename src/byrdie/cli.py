import os
import sys
from django.core.management import ManagementUtility
from django.conf import settings
import django
from byrdie import urls
from byrdie.utils import parse_imports, find_model_subclasses, register_discovered_models
from django.apps import apps
import importlib
def bootstrap_byrdie():
    """
    Sets up the Byrdie application context.
    """
    # We need to make sure the app is in the python path
    sys.path.insert(0, os.getcwd())
    # Minimal settings for Django to run
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='a-secret-key', # In a real app, this should be secret!
            ROOT_URLCONF='byrdie.urls', # Point to the new urls module
            INSTALLED_APPS=[
                'byrdie',
                'django.contrib.staticfiles',
                'app',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [
                        os.path.join(os.getcwd(), "components"),
                        os.path.join(os.getcwd(), "templates"),
                    ],
                    "APP_DIRS": True,
                }
            ],
            STATIC_URL="/static/",
            STATICFILES_DIRS=[os.path.join(os.getcwd(), "static")],
            MIGRATION_MODULES={'app': 'migrations'},
            SESSION_REMEMBER_ME_AGE=1209600,  # 2 weeks
        )
        django.setup()
    # This is a placeholder for a more sophisticated app discovery
    app_module = "app"
    # Dynamically import the app
    try:
        app = __import__(app_module)
        additional_modules = parse_imports(os.path.join(os.getcwd(), 'app.py'))
        errors = []
        imported_modules = [app]
        for module_name in additional_modules:
            try:
                imported_module = importlib.import_module(module_name)
                imported_modules.append(imported_module)
            except ImportError as e:
                errors.append(f"Failed to import {module_name}: {e}")
        if errors:
            print("Import errors occurred:", errors)
        print(f"Dynamically imported modules: {[m.__name__ for m in imported_modules]}")
        # Discover models from all imported modules first
        discovered_models = find_model_subclasses(imported_modules)
        # If no models discovered dynamically, fall back to initialize_models
        if not discovered_models and hasattr(app, 'initialize_models'):
            app.initialize_models()
            # Re-discover from app module after initialization
            app_discovered = find_model_subclasses([app])
            discovered_models.extend(app_discovered)
        print(f"Discovered {len(discovered_models)} models")
        # Register discovered models
        try:
            app_config = apps.get_app_config('app')
            register_discovered_models(discovered_models, app_config)
            print("Models registered successfully.")
        except Exception as e:
            print(f"Error registering models: {e}")
    except ImportError as e:
        print(f"Error importing app module: {e}")
        sys.exit(1)
def main():
    """
    A basic command-line interface for Byrdie.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m byrdie.cli <command>")
        sys.exit(1)
    command = sys.argv[1]
    if command == "runserver":
        bootstrap_byrdie()
        from byrdie.api import api
        urls.urlpatterns.extend(api.urls)
        # Default host and port
        host = "127.0.0.1"
        port = 8000
        if len(sys.argv) > 2:
            try:
                host, port_str = sys.argv[2].split(":")
                port = int(port_str)
            except ValueError:
                # Handle case where only port is given, or format is wrong
                try:
                    port = int(sys.argv[2])
                except ValueError:
                    print(f"Invalid address format: {sys.argv[2]}")
                    sys.exit(1)
        utility = ManagementUtility(['byrdie', 'runserver', f'{host}:{port}'])
        utility.execute()
    elif command == "makemigrations":
        bootstrap_byrdie()
        utility = ManagementUtility(['byrdie', 'makemigrations', 'app'])
        utility.execute()
    elif command == "migrate":
        bootstrap_byrdie()
        utility = ManagementUtility(['byrdie', 'migrate'])
        utility.execute()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
if __name__ == "__main__":
    main()

import os
import sys
from django.core.management import ManagementUtility
from django.conf import settings
import django
from byrdie import urls

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
                    "DIRS": [os.path.join(os.getcwd(), "components")],
                    "APP_DIRS": True,
                }
            ],
            STATIC_URL="/static/",
        )
        django.setup()

    # This is a placeholder for a more sophisticated app discovery
    app_module = "app"

    # Dynamically import the app
    try:
        __import__(app_module)
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
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

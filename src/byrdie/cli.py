import os
import sys
from typing import Optional
from django.core.management import ManagementUtility
from django.conf import settings
import django
import typer


app = typer.Typer()


def bootstrap_byrdie():
    """
    Sets up the Byrdie application context.
    """
    # We need to make sure the app is in the python path
    sys.path.insert(0, os.getcwd())

    # This is a placeholder for a more sophisticated app discovery
    app_module = "app"

    # Dynamically import the app
    try:
        __import__(app_module)
    except ImportError:
        print(f"Error: Could not find '{app_module}.py'. Please create one.")
        sys.exit(1)

    # Minimal settings for Django to run
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='a-secret-key', # In a real app, this should be secret!
            ROOT_URLCONF='byrdie.cli', # Point to this module
            INSTALLED_APPS=[
                'byrdie',
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
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
                    "APP_DIRS": True,
                }
            ],
        )
        django.setup()


@app.command()
def runserver(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="The host to listen on."),
    port: int = typer.Option(8000, "--port", "-p", help="The port to listen on."),
):
    """
    Starts the development server.
    """
    bootstrap_byrdie()
    utility = ManagementUtility(['byrdie', 'runserver', f'{host}:{port}'])
    utility.execute()


def main():
    app()


# This is needed for ROOT_URLCONF
urlpatterns = []


if __name__ == "__main__":
    main()

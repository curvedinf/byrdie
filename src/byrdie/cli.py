import os
import sys
from django.core.management import ManagementUtility
from django.conf import settings
import django

def main():
    """
    Runs the development server.
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

    # This is what `manage.py` does internally
    utility = ManagementUtility(sys.argv)
    utility.execute()

# This is needed for ROOT_URLCONF
urlpatterns = []

if __name__ == "__main__":
    main()

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from byrdie.cli import bootstrap_byrdie
bootstrap_byrdie()
from django.apps import apps
app_models = apps.get_models(app_label='app')
for model in app_models:
    print(model.__name__)

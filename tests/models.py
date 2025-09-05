from django.db import models
from byrdie.models import Model

class TestModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'

class SerializedModel(Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()
    secret = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'

class UnserializedModel(Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'

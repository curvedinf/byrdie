from django.db import models
from byrdie.models import Model, expose

class TestModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'


class ExposedModel(Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()
    exposed_fields = ["name", "value"]

    class Meta:
        app_label = 'tests'

    @expose
    def double(self):
        return self.value * 2


class Note(Model):
    content = models.TextField()
    components = ["card"]

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

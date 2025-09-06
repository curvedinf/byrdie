from django.db import models

def expose(func):
    """
    Decorator to expose a method to the frontend.
    """
    func._byrdie_exposed = True
    return func

class Model(models.Model):
    """
    Base model for Byrdie applications.
    """
    components = []
    exposed_fields = []

    class Meta:
        abstract = True


class Byrdie(Model):
    """
    An example model provided by the framework.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.db import models

class Model(models.Model):
    """
    Base model for Byrdie applications.
    """
    components = []

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

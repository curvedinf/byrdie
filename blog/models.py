from django.db import models
from byrdie.models import Model


class BlogPost(Model):
    title = models.CharField(max_length=200, expose=True)

    class Meta:
        pass

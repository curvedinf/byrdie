from byrdie.models import Model
from byrdie.api import route
from django.db import models


class Note(Model):
    text = models.CharField(max_length=255)

    class Meta:
        app_label = "app"

    def __str__(self):
        return self.text


@route("/")
def homepage(request):
    note = Note(text="Hello, Byrdie!")
    return {"note": note}

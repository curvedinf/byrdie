from byrdie.api import route
from django.db import models
import blog.models
import blog.views
Note = None
def initialize_models():
    global Note
    from byrdie.models import Model, expose
    class TmpNote(Model):
        text = models.CharField(max_length=255)
        exposed_fields = ['text']
        class Meta:
            app_label = "app"
        def __str__(self):
            return self.text
        @expose
        def clear_text(self):
            self.text = ""
            return {"text": self.text}
        @expose
        def update_text(self, new_text=""):
            self.text = new_text
            return {"text": self.text}
    Note = TmpNote
@route("/")
def homepage(request):
    note, _ = Note.objects.get_or_create(pk=1, defaults={'text': "Hello, Byrdie!"})
    return {"note": note}

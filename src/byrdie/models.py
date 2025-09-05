from django.db import models
from django.db.models.base import ModelBase
from pydantic import create_model as create_pydantic_model
from byrdie.schemas import Schema
from byrdie.utils import FIELD_TYPE_MAPPING
import datetime


def field_init_wrapper(original_init):
    def new_init(self, *args, **kwargs):
        self.expose = kwargs.pop('expose', False)
        original_init(self, *args, **kwargs)
    return new_init

# Monkey-patch the Field classes
for field_class in FIELD_TYPE_MAPPING.keys():
    field = getattr(models, field_class)
    field.__init__ = field_init_wrapper(field.__init__)

class ByrdieModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        # Don't do anything for abstract models or proxy models
        if new_class._meta.abstract or new_class._meta.proxy:
            new_class._default_schema = None
            return new_class

        pydantic_fields = {}
        for field in new_class._meta.fields:
            if getattr(field, 'expose', False):
                field_type = field.get_internal_type()
                python_type = FIELD_TYPE_MAPPING.get(field_type, str)
                pydantic_fields[field.name] = (python_type, ...)

        if pydantic_fields:
            # Create the Pydantic model
            default_schema = create_pydantic_model(
                f"{name}DefaultSchema",
                **pydantic_fields,
                __base__=Schema
            )
            new_class._default_schema = default_schema
        else:
            new_class._default_schema = None

        return new_class


class Model(models.Model, metaclass=ByrdieModelBase):
    components = []

    class Meta:
        abstract = True


class Byrdie(Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

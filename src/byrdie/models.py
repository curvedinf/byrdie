from django.db import models
from django.db.models.base import ModelBase
from pydantic import create_model as create_pydantic_model
from byrdie.schemas import Schema
from byrdie.utils import FIELD_TYPE_MAPPING
import datetime


class ByrdieModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        # Extract our custom 'expose' attribute from Meta before Django sees it
        meta = attrs.get('Meta')
        exposed_fields = []
        if meta:
            exposed_fields = getattr(meta, 'expose', [])
            if hasattr(meta, 'expose'):
                delattr(meta, 'expose')

        new_class = super().__new__(cls, name, bases, attrs)

        # Don't do anything for abstract models or proxy models
        if new_class._meta.abstract or new_class._meta.proxy:
            new_class._default_schema = None
            return new_class

        if exposed_fields:
            pydantic_fields = {}
            for field in new_class._meta.fields:
                if field.name in exposed_fields:
                    field_type = field.get_internal_type()
                    python_type = FIELD_TYPE_MAPPING.get(field_type, str)
                    pydantic_fields[field.name] = (python_type, ...)

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
    class Meta:
        abstract = True


class Byrdie(Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

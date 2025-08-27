from pydantic import BaseModel as PydanticBaseModel, ConfigDict

class BaseModel(PydanticBaseModel):
    """
    The base model for all Byrdie schemas.
    """
    model_config = ConfigDict(
        from_attributes=True,
    )

from pydantic._internal._model_construction import ModelMetaclass
from byrdie.utils import FIELD_TYPE_MAPPING


from pydantic._internal._model_construction import ModelMetaclass
from byrdie.utils import FIELD_TYPE_MAPPING

class Schema(BaseModel):
    """
    The base class for all Byrdie schemas.
    """
    pass

class ModelSchemaBase(ModelMetaclass):
    def __new__(cls, name, bases, attrs, **kwargs):
        meta = attrs.get('Meta')

        if meta and hasattr(meta, 'model') and hasattr(meta, 'fields'):
            model = meta.model
            fields = meta.fields

            pydantic_fields = {}
            for field_name in fields:
                django_field = model._meta.get_field(field_name)
                field_type = django_field.get_internal_type()
                python_type = FIELD_TYPE_MAPPING.get(field_type, str)
                pydantic_fields[field_name] = python_type

            if '__annotations__' not in attrs:
                attrs['__annotations__'] = {}

            for field_name, python_type in pydantic_fields.items():
                attrs['__annotations__'][field_name] = python_type

        if not any(issubclass(b, Schema) for b in bases):
            bases = (Schema,) + bases

        return super().__new__(cls, name, bases, attrs, **kwargs)


class ModelSchema(Schema, metaclass=ModelSchemaBase):
    """
    A schema that is automatically generated from a Django model.
    """
    class Meta:
        abstract = True

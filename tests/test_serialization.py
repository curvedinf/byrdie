import pytest
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from byrdie.schemas import Schema, ModelSchema
from typing import List
from tests.models import SerializedModel, UnserializedModel
from byrdie.api import Api

def test_serialization_single_object(rf):
    api = Api()
    class MySchema(Schema):
        name: str
        age: int
    @api.route("/get/single")
    def get_single(request) -> MySchema:
        return MySchema(name="Test", age=100)
    request = rf.get("/")
    view = api.router.get_view("/get/single")
    response = view(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == {"name": "Test", "age": 100}

def test_serialization_from_dict(rf):
    api = Api()
    class MySchema(Schema):
        name: str
        age: int
    @api.route("/get/single/from/dict")
    def get_single_from_dict(request) -> MySchema:
        return {"name": "Test", "age": 100}
    request = rf.get("/")
    view = api.router.get_view("/get/single/from/dict")
    response = view(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == {"name": "Test", "age": 100}

def test_serialization_list_of_objects(rf):
    api = Api()
    class MySchema(Schema):
        name: str
        age: int
    @api.route("/get/list")
    def get_list(request) -> List[MySchema]:
        return [MySchema(name="Test1", age=1), MySchema(name="Test2", age=2)]
    request = rf.get("/")
    view = api.router.get_view("/get/list")
    response = view(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == [{"name": "Test1", "age": 1}, {"name": "Test2", "age": 2}]

def test_no_serialization_for_non_schema(rf):
    api = Api()
    @api.route("/get/string")
    def get_string(request) -> str:
        return "Hello, World!"
    request = rf.get("/")
    view = api.router.get_view("/get/string")
    response = view(request)
    assert isinstance(response, HttpResponse)
    assert not isinstance(response, JsonResponse)
    assert response.content == b"Hello, World!"

def test_default_serialization_single_model_no_db(rf):
    api = Api()

    class MyObject:
        _default_schema = None
        def __init__(self, name, value, secret):
            self.name = name
            self.value = value
            self.secret = secret

    # Mocking a model with a default schema
    from byrdie.schemas import Schema
    class MyObjectSchema(Schema):
        name: str
        value: int
    MyObject._default_schema = MyObjectSchema


    @api.route("/get/model")
    def get_model(request):
        return MyObject(name="Test Model", value=123, secret="Do not expose")

    request = rf.get("/")
    view = api.router.get_view("/get/model")
    response = view(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == {"name": "Test Model", "value": 123}
    assert "secret" not in data

@pytest.mark.django_db
def test_explicit_schema_overrides_default(rf):
    api = Api()
    class ExplicitSchema(Schema):
        name: str
    @api.route("/get/model/explicit")
    def get_model_explicit(request) -> ExplicitSchema:
        return SerializedModel(name="Test Model", value=123, secret="Do not expose")
    request = rf.get("/")
    view = api.router.get_view("/get/model/explicit")
    response = view(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == {"name": "Test Model"}
    assert "value" not in data

def test_simple_registration_in_serialization_file():
    api = Api()
    @api.route("/test")
    def my_test_view(request):
        pass
    view = api.router.get_view("/test")
    assert view is not None


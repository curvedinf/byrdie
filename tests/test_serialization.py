import pytest
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from pydantic import BaseModel
from typing import List

import byrdie.routing
from byrdie.routing import route, Router

# Fixture to reset the global router before each test
@pytest.fixture(autouse=True)
def reset_router():
    new_router = Router()
    original_router = byrdie.routing.router
    byrdie.routing.router = new_router
    yield
    byrdie.routing.router = original_router


class MySchema(BaseModel):
    name: str
    age: int


def test_schema_detection_single_object():
    @route()
    def get_single() -> MySchema:
        pass

    assert get_single.response_schema == MySchema

def test_schema_detection_list_of_objects():
    @route()
    def get_list() -> List[MySchema]:
        pass

    assert get_list.response_schema == List[MySchema]

def test_no_schema_detection_when_no_hint():
    @route()
    def no_schema():
        pass

    assert no_schema.response_schema is None

def test_schema_detection_with_non_schema_return_type():
    @route()
    def other_return_type() -> str:
        pass

    assert other_return_type.response_schema == str


def test_serialization_single_object(rf):
    @route()
    def get_single(request) -> MySchema:
        return MySchema(name="Test", age=100)

    request = rf.get("/")
    response = get_single(request)

    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == {"name": "Test", "age": 100}

def test_serialization_list_of_objects(rf):
    @route()
    def get_list(request) -> List[MySchema]:
        return [MySchema(name="Test1", age=1), MySchema(name="Test2", age=2)]

    request = rf.get("/")
    response = get_list(request)

    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data == [{"name": "Test1", "age": 1}, {"name": "Test2", "age": 2}]

def test_no_serialization_for_non_schema(rf):
    @route()
    def get_string(request) -> str:
        return "Hello, World!"

    request = rf.get("/")
    response = get_string(request)

    assert isinstance(response, HttpResponse)
    assert not isinstance(response, JsonResponse)
    assert response.content == b"Hello, World!"

def test_no_serialization_when_no_hint(rf):
    @route()
    def get_plain(request):
        return "Plain text"

    request = rf.get("/")
    response = get_plain(request)

    assert isinstance(response, HttpResponse)
    assert not isinstance(response, JsonResponse)
    assert response.content == b"Plain text"

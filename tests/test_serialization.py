import pytest
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

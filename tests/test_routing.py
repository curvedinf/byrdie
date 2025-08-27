import pytest
import json
from byrdie.api import Api, action
from byrdie.schemas import Schema, ModelSchema
from django.http import JsonResponse, HttpResponse
from tests.models import TestModel


def test_explicit_path():
    api = Api()
    @api.route("/explicit/path")
    def my_view(request):
        pass
    view = api.router.get_view("/explicit/path")
    assert view is not None

def test_implicit_path_with_parentheses():
    api = Api()
    @api.route()
    def my__implicit__view(request):
        pass
    view = api.router.get_view("/my/implicit/view")
    assert view is not None

def test_implicit_path_no_parentheses():
    api = Api()
    @api.route
    def another__implicit__view(request):
        pass
    view = api.router.get_view("/another/implicit/view")
    assert view is not None

def test_duplicate_route_raises_error():
    api = Api()
    @api.route("/duplicate")
    def view1(request):
        pass
    with pytest.raises(ValueError, match="Route for path '/duplicate' is already registered."):
        @api.route("/duplicate")
        def view2(request):
            pass

def test_root_path():
    api = Api()
    @api.route("/")
    def root_view(request):
        pass
    view = api.router.get_view("/")
    assert view is not None

def test_path_with_trailing_slash_in_name():
    api = Api()
    @api.route
    def trailing__slash__(request):
        pass
    view = api.router.get_view("/trailing/slash")
    assert view is not None

def test_get_nonexistent_view():
    api = Api()
    assert api.router.get_view("/nonexistent") is None

def test_api_prefixing_with_explicit_path():
    api = Api()
    @api.route("/explicit/path", api=True)
    def my_api_view(request):
        pass
    view = api.router.get_view("/api/explicit/path")
    assert view is not None

def test_api_prefixing_with_implicit_path():
    api = Api()
    @api.route(api=True)
    def my__implicit__api__view(request):
        pass
    view = api.router.get_view("/api/my/implicit/api/view")
    assert view is not None

def test_security_attributes():
    api = Api()
    def dummy_permission_check(user):
        return True
    @api.route("/secure", is_authenticated=True, has_permissions=dummy_permission_check)
    def secure_view(request):
        pass
    view = api.router.get_view("/secure")
    assert secure_view.is_authenticated is True
    assert secure_view.has_permissions == dummy_permission_check


def test_schema_classmethod_route():
    api = Api()
    class TestSchema(Schema):
        @classmethod
        @action()
        def list(cls, request):
            return JsonResponse([{"id": 1}, {"id": 2}], safe=False)
    api.add_schema(TestSchema)
    view = api.router.get_view("/test/list")
    assert view is not None

def test_schema_classmethod_route_custom_path():
    api = Api()
    class TestSchema(Schema):
        @classmethod
        @action("/custom")
        def custom_list(cls, request):
            return HttpResponse("Custom")
    api.add_schema(TestSchema)
    view = api.router.get_view("/test/custom")
    assert view is not None

@pytest.mark.django_db
def test_model_schema_instance_method_route(rf):
    api = Api()
    class TestModelSchema(ModelSchema):
        class Meta:
            model = TestModel
            fields = ['id', 'name']
        @action()
        def retrieve(self, request, pk: int):
            return JsonResponse(self.model_dump())
    api.add_schema(TestModelSchema)
    instance = TestModel.objects.create(name="Test Instance")
    view = api.router.get_view("/testmodel/<int:pk>/retrieve")
    assert view is not None
    request = rf.get("/")
    response = view(request, pk=instance.pk)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['name'] == "Test Instance"

def test_simple_registration():
    api = Api()
    @api.route("/test")
    def my_test_view(request):
        pass
    view = api.router.get_view("/test")
    assert view is not None

@pytest.mark.django_db
def test_model_schema_instance_method_route_custom_path(rf):
    api = Api()
    class TestModelSchema(ModelSchema):
        class Meta:
            model = TestModel
            fields = ['id', 'name']
        @action("/do-something")
        def action_view(self, request, pk: int):
            return HttpResponse(f"Action on {self.name}")
    api.add_schema(TestModelSchema)
    instance = TestModel.objects.create(name="Test Instance")
    view = api.router.get_view("/testmodel/<int:pk>/do-something")
    assert view is not None
    request = rf.get("/")
    response = view(request, pk=instance.pk)
    assert response.status_code == 200
    assert response.content == b"Action on Test Instance"


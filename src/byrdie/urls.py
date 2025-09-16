from django.urls import path
from .views import call_exposed_method

urlpatterns = [
    path('byrdie/call/<str:app_label>/<str:model_name>/<int:pk>/<str:method_name>/', call_exposed_method, name='byrdie-call'),
]

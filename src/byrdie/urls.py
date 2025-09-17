from django.urls import path
from .views import call_exposed_method
from .auth import login

urlpatterns = [
    path('byrdie/call/<str:app_label>/<str:model_name>/<int:pk>/<str:method_name>/', call_exposed_method, name='byrdie-call'),
    path('login/', login, name='login'),
]

from django.urls import path
from .views import index, restricted_access, register

urlpatterns = [
    path('', index, name='index'),
    path('restricted/', restricted_access, name='restricted_access'),
    path('register/', register, name='register'),
]
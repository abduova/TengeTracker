from django.urls import path
from .views import register, login, logout, test_auth

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('test/', test_auth),
]
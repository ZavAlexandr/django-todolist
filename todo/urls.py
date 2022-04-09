from django.urls import path
from .views import *


urlpatterns = [
    path('', signup_user, name='signup_user'),
]

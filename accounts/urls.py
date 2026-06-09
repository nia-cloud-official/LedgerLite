from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path("register/", views.register, name="register"),
]
from django.urls import path

from . import views

app_name = "GearsPilot"

urlpatterns = [
path('', views.index, name = "index"),
]

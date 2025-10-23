from django.urls import path
from . import views

urlpatterns = [
    path("analyze-text/", views.analyze_text, name="analyze_text"),
    path("analyze-image/", views.analyze_image, name="analyze_image"),
]

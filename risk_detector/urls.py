from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/students/", include("students.urls")),
    path('teachers/', include('teachers.urls')),
    path("gamification/", include("gamification.urls")),
    path("ai/", include("ai_detection.urls")),



]

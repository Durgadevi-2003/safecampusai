# from django.urls import path
# from . import views

# urlpatterns = [
#     path("upload/", views.upload_behavior, name="upload_behavior"),
#     path("predict/<str:student_id>/", views.predict_student, name="predict_student"),
#     path("history/<str:student_id>/", views.prediction_history, name="prediction_history"),
# ]

# new

from django.urls import path
from . import views

urlpatterns = [
     # Custom Auth
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("add/", views.add_student, name="add_student"),
    path("upload/", views.upload_behavior, name="upload_behavior"),
    path("history/<str:student_id>/", views.prediction_history, name="prediction_history"),
    path("list/", views.student_list, name="student_list"),
     path("dashboard/", views.student_dashboard, name="student_dashboard"),
     path('add-behavior/', views.add_daily_behavior, name='add_daily_behavior'),
]


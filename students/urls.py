from django.urls import path
from . import views

urlpatterns = [
     # Custom Auth
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("add/", views.add_student, name="add_student"),
    path("upload/", views.upload_behavior, name="upload_behavior"),
#     path("success/", views.behavior_success, name="behavior_success"),
    path("history/<str:student_id>/", views.prediction_history, name="prediction_history"),
    path("list/", views.student_list, name="student_list"),
     path("dashboard/", views.student_dashboard, name="student_dashboard"),
     path('add-behavior/', views.add_daily_behavior, name='add_daily_behavior'),
     
     path("success/<str:student_id>/", views.behavior_success, name="behavior_success"),
# path("history/<str:student_id>/", views.prediction_history, name="prediction_history"),
     path("chatbot/", views.ai_chatbot, name="ai_chatbot"),
     
     path("addiction/add/", views.add_addiction_entry, name="addiction_add"),
path("addiction/dashboard/", views.addiction_dashboard, name="addiction_dashboard"),
path("addiction/data/<str:period>/", views.addiction_data, name="addiction_data"),
path("addiction/pdf/", views.addiction_report_pdf, name="addiction_report_pdf"),
path('notifications/', views.student_notifications, name='student_notifications'),


]


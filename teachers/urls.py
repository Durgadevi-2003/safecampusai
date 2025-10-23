# teachers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('predictions/overview/', views.risk_overview, name='prediction_overview'),
    path('reports/csv/', views.export_students_csv, name='export_students_csv'),
    path('reports/pdf/', views.export_students_pdf, name='export_students_pdf'),
    path("drug-alerts/", views.drug_alerts, name="drug_alerts"),
     path('schedule/<int:student_id>/', views.schedule_counseling, name='schedule_counseling'),

    
]

# teachers/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from students.models import Student, RiskPrediction

# @login_required
# def teacher_dashboard(request):
#     # Get all students and their latest risk predictions
#     students_data = []
#     for student in Student.objects.all():
#         latest_pred = RiskPrediction.objects.filter(student=student).order_by('-created_at').first()
#         students_data.append({
#             "student": student,
#             "latest_pred": latest_pred,
#         })
#     return render(request, "teachers/dashboard.html", {"students_data": students_data})

 
@login_required
def teacher_dashboard(request):
    students_data = []
    for student in Student.objects.all():
        latest_pred = RiskPrediction.objects.filter(student=student).order_by('-timestamp').first()
        students_data.append({
            "student": student,
            "latest_pred": latest_pred,
        })
    return render(request, "teachers/dashboard.html", {"students_data": students_data})

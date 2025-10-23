# teachers/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from students.models import Student, RiskPrediction
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse, Http404
from students.models import Student, RiskPrediction,AddictionEntry
import csv
from django.template.loader import render_to_string
import datetime
from students.models import DrugAlert
from django.shortcuts import render, redirect, get_object_or_404
from .models import CounselingSession
from django.contrib import messages
from students.models import StudentNotification
 


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
 
@login_required
def risk_overview(request):
    # Option A: simple loop (works reliably and clear)
    counts = {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0, "No Data": 0}

    students = Student.objects.all()

    for student in students:
        latest = RiskPrediction.objects.filter(student=student).order_by('-timestamp').first()
        if not latest:
            counts["No Data"] += 1
        else:
            label = latest.risk_label or "No Data"
            # normalize label text to one of the buckets
            if "high" in label.lower():
                counts["High Risk"] += 1
            elif "medium" in label.lower():
                counts["Medium Risk"] += 1
            elif "low" in label.lower():
                counts["Low Risk"] += 1
            else:
                counts["No Data"] += 1

    # Prepare data arrays for Chart.js
    labels = list(counts.keys())
    values = [counts[k] for k in labels]

    # Optional metrics
    total_students = students.count()
    high_pct = (counts["High Risk"] / total_students * 100) if total_students else 0

    context = {
        "labels": labels,           # ["High Risk", "Medium Risk", "Low Risk", "No Data"]
        "values": values,           # [5, 10, 20, 3]
        "total_students": total_students,
        "high_pct": round(high_pct, 1),
    }
    return render(request, "teachers/risk_overview.html", context)
 
def get_student_latest_predictions():
    students = Student.objects.all().order_by('student_id')
    rows = []
    for s in students:
        latest = RiskPrediction.objects.filter(student=s).order_by('-timestamp').first()
        rows.append({
            "student_id": s.student_id,
            "name": s.name or s.user.username if getattr(s, "user", None) else "",
            "email": s.email or (s.user.email if getattr(s, "user", None) else ""),
            "latest_label": latest.risk_label if latest else "",
            "latest_score": latest.risk_score if latest else "",
            "timestamp": latest.timestamp if latest else "",
        })
    return rows

@login_required
def export_students_csv(request):
    rows = get_student_latest_predictions()

    # Create the HttpResponse object with CSV headers.
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"student_risk_report_{now}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    # Header
    writer.writerow(["student_id", "name", "email", "latest_label", "latest_score", "timestamp"])
    # Rows
    for r in rows:
        writer.writerow([
            r["student_id"],
            r["name"],
            r["email"],
            r["latest_label"],
            r["latest_score"],
            r["timestamp"],
        ])

    return response
@login_required
def export_students_pdf(request):
    rows = get_student_latest_predictions()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = {
        "rows": rows,
        "now": now,
        "total": len(rows),
    }

    # Render HTML template to string
    html = render_to_string("teachers/report.html", context)

    try:
        # xhtml2pdf
        from xhtml2pdf import pisa
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_risk_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error creating PDF", status=500)
        return response
    except Exception as e:
        # fallback message if library missing
        return HttpResponse("PDF generation requires xhtml2pdf. Install with `pip install xhtml2pdf`.", status=500)
 
@login_required
def drug_alerts(request):
    alerts = DrugAlert.objects.select_related("student").order_by("-timestamp")
    return render(request, "teachers/drug_alerts.html", {"alerts": alerts})

 
@login_required
def schedule_counseling(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        mode = request.POST.get("mode")
        session_date = request.POST.get("session_date")
        notes = request.POST.get("notes")
        date = request.POST.get("date")
        time = request.POST.get("time")
    
        CounselingSession.objects.create(
            teacher=request.user,
            student=student,
            session_date=session_date,
            mode=mode,
            notes=notes
        )
        StudentNotification.objects.create(
              student=student,
              message=f"A counseling session has been scheduled on {date} at {time}. Please be present on time."
        )
        messages.success(request, f"Counseling session scheduled for {student.name or student.user.username}!")
        return redirect("drug_alerts")

    return render(request, "teachers/schedule_counseling.html", {"student": student})



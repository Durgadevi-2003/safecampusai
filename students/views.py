from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Student, DailyBehavior, RiskPrediction,AddictionEntry,StudentNotification
from .forms import StudentForm, DailyBehaviorForm,AddictionEntryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User 
import joblib
import json
import numpy as np
import tensorflow as tf
import os
import xgboost as xgb
from tensorflow.keras.models import load_model
import random 
from gamification.models import Streak, Leaderboard
from .chatbot_nlp import mental_health_reply
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Avg
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from xhtml2pdf import pisa
import io
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from ai_detection.text_detector import detect_drug_text
 
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("student_dashboard")   # redirect to student dashboard
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "auth/login.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=username, password=password)
            # Create linked Student profile
            Student.objects.create(
            user=user,                 # 🔑 link to user
            student_id=username,       # or generate unique roll no
            name=username              # you can add email, dept, etc
            )
            login(request, user)
            return redirect("students/student_list")   # go to dashboard after signup

    return render(request, "auth/signup.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")   # back to login page

 
# Load models once
scaler = joblib.load("models/scaler.joblib")
lstm_model = tf.keras.models.load_model("models/student_behavior_lstm_supervised.h5")

@login_required
def student_dashboard(request):
    student, created = Student.objects.get_or_create(user=request.user)

    latest_behavior = DailyBehavior.objects.filter(student=student).order_by("-date").first()
    latest_prediction = None
    behaviors = []
    predictions = []
    streak, _ = Streak.objects.get_or_create(user=request.user)
    streak.update_streak()

    leaderboard, _ = Leaderboard.objects.get_or_create(user=request.user)
    leaderboard.add_points(10)  # +10 points for daily login

    if latest_behavior:
        # ✅ last 7 days data (oldest → newest)
        behaviors = DailyBehavior.objects.filter(student=student).order_by("date")[:7]
        predictions = RiskPrediction.objects.filter(student=student).order_by("timestamp")[:7]

        if len(behaviors) == 7:
            # build feature matrix (7 days × 8 features)
            features = np.array([
                [
                    b.screen_time_hrs,
                    b.night_usage_hrs,
                    b.sleep_hours,
                    b.app_social_hrs,
                    b.app_entertainment_hrs,
                    b.app_education_hrs,
                    int(b.late_sleep_flag),
                    int(b.low_sleep_flag),
                ]
                for b in reversed(behaviors)
            ])

            # scale and predict
            features_scaled = scaler.transform(features)
            features_reshaped = features_scaled.reshape((1, 7, 8))
            prediction = lstm_model.predict(features_reshaped, verbose=0)
            risk_score = float(prediction[0][0])
            risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

            # save prediction
            latest_prediction = RiskPrediction.objects.create(
                student=student,
                risk_label=risk_label,
                risk_score=risk_score,
                metadata={"model": "LSTM", "days_used": 7}
            )

    # ✅ prepare data for charts
    behavior_dates = [b.date.strftime("%b %d") for b in behaviors]
    screen_times = [float(b.screen_time_hrs) for b in behaviors]
    risk_scores = [float(p.risk_score) for p in predictions] if predictions else []
    # ✅ New: Daily Care Tips
    daily_tips = [
        "💧 Drink at least 8 glasses of water daily to stay hydrated.",
        "🧠 Take a 5-min break after every hour of study to refresh your mind.",
        "😴 Maintain 7–8 hours of sleep for better focus and memory.",
        "🚶‍♂️ Go for a short walk during study breaks to reduce stress.",
        "📵 Avoid screen time 1 hour before bed to improve sleep quality.",
        "🥗 Eat light meals during study hours for better concentration.",
        "💬 Stay connected with friends or mentors if you feel stressed.",
        "🪴 Keep your study space clean and ventilated for fresh energy.",
        "📅 Plan your daily goals each morning to reduce anxiety.",
        "🎧 Listen to soft instrumental music while studying to improve focus."
    ]
    selected_tip = random.choice(daily_tips)
    
    # Example badge logic
    if streak.current_streak == 5:
        from gamification.models import Badge, UserBadge
        badge, _ = Badge.objects.get_or_create(name="🔥 5-Day Streak", defaults={"description": "Logged in for 5 days straight!", "icon": "🔥"})
        UserBadge.objects.get_or_create(user=request.user, badge=badge)
    context = {
        "student": student,
        "latest_behavior": latest_behavior,
        "latest_prediction": latest_prediction,
        "created": created,
        "behaviors": behaviors,
        "predictions": predictions,
        "dates": behavior_dates,
        "screen_times": screen_times,
        "risk_scores": risk_scores,
        "daily_tip": selected_tip,  # 🆕 Add this
        "streak": streak,
        "leaderboard": leaderboard,
    }

    return render(request, "students/dashboard.html", context)


@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("student_list")  # redirect to list page after saving
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form})
 
@login_required
def upload_behavior(request):
    if request.method == "POST":
        form = DailyBehaviorForm(request.POST)
        if form.is_valid():
            # form.save()
            behavior = form.save()
            student = behavior.student  # ✅ get related student instance
            return redirect("behavior_success", student_id=student.student_id)
  # you can create a success page
    else:
        form = DailyBehaviorForm()
    return render(request, "students/behavior_form.html", {"form": form})
# @login_required
# def behavior_success(request):
#     return render(request, "students/behavior_success.html")
@login_required
def behavior_success(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(request, "students/behavior_success.html", {"student": student})

@login_required
def prediction_history(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    predictions = RiskPrediction.objects.filter(student=student).order_by("-timestamp")
    return render(
        request,
        "students/history.html",
        {"student": student, "predictions": predictions},
    )
 
@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "students/student_list.html", {"students": students})

 
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")  # your models folder

# Load models
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
lstm_model = load_model(os.path.join(MODEL_DIR, "student_behavior_lstm_supervised.h5"))
feature_extractor = load_model(os.path.join(MODEL_DIR, "student_behavior_feature_extractor.h5"))
label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.joblib"))

SEQUENCE_LENGTH = 7
FEATURE_COUNT = 8

# =========================
# Utility: Pad/truncate to 7 days
# =========================
def prepare_input(data, sequence_length=SEQUENCE_LENGTH, feature_count=FEATURE_COUNT):
    arr = np.array(data, dtype=float)
    if arr.shape[0] < sequence_length:
        padding = np.zeros((sequence_length - arr.shape[0], feature_count))
        arr = np.vstack([padding, arr])
    elif arr.shape[0] > sequence_length:
        arr = arr[-sequence_length:]
    return arr.reshape(1, sequence_length, feature_count)

# =========================
# Main view
# =========================
@login_required
def add_daily_behavior(request):
    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = DailyBehaviorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Save or update behavior for today
            behavior, created = DailyBehavior.objects.update_or_create(
                student=student,
                date=data["date"],
                defaults={
                    "screen_time_hrs": data["screen_time_hrs"],
                    "night_usage_hrs": data["night_usage_hrs"],
                    "sleep_hours": data["sleep_hours"],
                    "app_social_hrs": data["app_social_hrs"],
                    "app_entertainment_hrs": data["app_entertainment_hrs"],
                    "app_education_hrs": data["app_education_hrs"],
                    "late_sleep_flag": data["late_sleep_flag"],
                    "low_sleep_flag": data["low_sleep_flag"],
                }
            )

            # Fetch latest 7 days for prediction
            behaviors = DailyBehavior.objects.filter(student=student).order_by("-date")[:SEQUENCE_LENGTH]

            if behaviors.exists():
                # Oldest → newest
                features = np.array([
                    [
                        b.screen_time_hrs,
                        b.night_usage_hrs,
                        b.sleep_hours,
                        b.app_social_hrs,
                        b.app_entertainment_hrs,
                        b.app_education_hrs,
                        int(b.late_sleep_flag),
                        int(b.low_sleep_flag),
                    ]
                    for b in reversed(behaviors)
                ])

                # Scale + pad
                features_scaled = scaler.transform(features)
                features_prepared = prepare_input(features_scaled, SEQUENCE_LENGTH, FEATURE_COUNT)

                # Predict LSTM risk
                prediction = lstm_model.predict(features_prepared, verbose=0)
                risk_score = float(prediction[0][0])
                risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

                # Save prediction
                RiskPrediction.objects.create(
                    student=student,
                    risk_label=risk_label,
                    risk_score=risk_score,
                    metadata={"model": "LSTM", "days_used": features.shape[0]}
                )

            return redirect("student_dashboard")
    else:
        form = DailyBehaviorForm()

    return render(request, "students/add_behavior.html", {"form": form})

 

# def ai_chatbot(request):
    # query = request.GET.get("q", "").lower()

    # tips = [
    #     "💧 Drink water regularly to stay alert during classes!",
    #     "📚 Take a 5-minute break after every hour of study.",
    #     "😴 Try to sleep at least 7-8 hours a day.",
    #     "🌿 Go for a short walk to reduce screen fatigue.",
    #     "💭 Practice deep breathing for 2 minutes to reduce stress.",
    #     "🕒 Keep a fixed study schedule and stick to it."
    # ]

    # responses = {
    #     "hey":"Hello how can i help you",
    #     "stress": "Try meditation or deep breathing for 5 minutes. It calms your mind.",
    #     "study": "Study smart — 50 minutes focus + 10 minutes break is best.",
    #     "sleep": "Avoid screen time before bed and get at least 7 hours of sleep.",
    #     "phone": "Keep your phone away while studying for better concentration.",
    #     "exam": "Don’t panic! Revise key points and take breaks to refresh your mind.",
    # }

    # reply = None
    # for keyword, ans in responses.items():
    #     if keyword in query:
    #         reply = ans
    #         break

    # if not reply:
    #     reply = random.choice(tips)

    # return JsonResponse({"reply": reply})

@login_required
def ai_chatbot(request):
    query = request.GET.get("q", "")
    student = Student.objects.get(user=request.user)

    if not query:
        return JsonResponse({"reply": f"Hi {student.name} 👋 How are you feeling today?"})

    # Mental health AI
    reply = mental_health_reply(query, student.name)

    # Drug AI Detection
    detection = detect_drug_text(query, student)

    return JsonResponse({
        "reply": reply,
        "risk_label": detection["label"],
        "risk_score": detection["score"],
        "detected": detection["detected_words"],
    })

 
@login_required
def add_addiction_entry(request):
    # ensure student profile exists and is linked
    student = getattr(request.user, "student", None)
    if not student:
        return redirect("student_dashboard")

    if request.method == "POST":
        form = AddictionEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = student
            try:
                entry.save()
                # 🚨 Emergency check
                if entry.craving_level >= 9 and entry.mood <= 2:
                # Optional alert to teacher (counselor)
                   send_mail(
                     subject="🚨 Emergency Alert: Student Needs Attention",
                     message=f"Student {student.name} has reported high craving ({entry.craving_level}) and low mood ({entry.mood}).",
                     from_email="safecampusai@gmail.com",
                     recipient_list=["teacher@example.com"],  # update your counselor email
                   )
                   messages.error(request, "⚠️ Critical condition detected! Counselor has been notified.")
                else:
                   messages.success(request, "✅ Progress recorded successfully!")
            except Exception as e:
                form.add_error(None, "Entry for this date already exists or invalid.")
            else:
                return redirect("addiction_dashboard")
    else:
        # pre-fill date today
        form = AddictionEntryForm(initial={"date": timezone.localdate()})
    return render(request, "students/addiction_form.html", {"form": form})

@login_required
def addiction_dashboard(request):
    student = getattr(request.user, "student", None)
    logs = AddictionEntry.objects.filter(student=student).order_by("date")

    if not student:
        return redirect("student_dashboard")

    # summary stats
    entries = AddictionEntry.objects.filter(student=student).order_by("-date")[:30]
    avg_mood = entries.aggregate(Avg("mood"))["mood__avg"] or 0
    avg_craving = entries.aggregate(Avg("craving_level"))["craving_level__avg"] or 0

    # milestones (example)
    total_days = AddictionEntry.objects.filter(student=student).count()
    milestones = {
        "entries_recorded": total_days,
        "good_days": AddictionEntry.objects.filter(student=student, mood__gte=7, craving_level__lte=4).count(),
    }
    # Chart generation (mood & craving)
    dates = [l.date.strftime("%d-%b") for l in logs]
    mood = [l.mood for l in logs]
    craving = [l.craving_level for l in logs]

    plt.figure(figsize=(6, 3))
    plt.plot(dates, mood, label="Mood", marker="o")
    plt.plot(dates, craving, label="Craving", marker="x")
    plt.legend()
    plt.title("Recovery Progress")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return render(request, "students/addiction_dashboard.html", {
        "student": student,
        "avg_mood": round(avg_mood,1),
        "avg_craving": round(avg_craving,1),
        "entries": entries,
        "milestones": milestones,
        "logs": logs, 
        "chart": chart_data
    })

@login_required
def addiction_data(request, period="30d"):
    """
    Returns JSON: labels[], mood[], craving[], recovery[]
    periods: '7d', '30d', '90d', 'monthly'
    """
    student = getattr(request.user, "student", None)
    if not student:
        return JsonResponse({"error": "No student profile"}, status=400)

    today = date.today()
    if period == "7d":
        start = today - timedelta(days=6)
        qs = AddictionEntry.objects.filter(student=student, date__gte=start).order_by("date")
        labels = []
        mood = []
        craving = []
        recovery = []
        for d in (start + timedelta(days=i) for i in range(7)):
            labels.append(d.strftime("%b %d"))
            e = qs.filter(date=d).first()
            if e:
                mood.append(e.mood)
                craving.append(e.craving_level)
                recovery.append(e.recovery_score)
            else:
                mood.append(None)
                craving.append(None)
                recovery.append(None)
    elif period in ("30d", "90d"):
        days = 30 if period=="30d" else 90
        start = today - timedelta(days=days-1)
        qs = AddictionEntry.objects.filter(student=student, date__gte=start).order_by("date")
        labels = []
        mood = []
        craving = []
        recovery = []
        for d in (start + timedelta(days=i) for i in range(days)):
            labels.append(d.strftime("%b %d"))
            e = qs.filter(date=d).first()
            if e:
                mood.append(e.mood)
                craving.append(e.craving_level)
                recovery.append(e.recovery_score)
            else:
                mood.append(None)
                craving.append(None)
                recovery.append(None)
    elif period == "monthly":
        # aggregate by month for last 6 months
        labels=[]
        mood=[]
        craving=[]
        recovery=[]
        for i in range(5, -1, -1):
            first = (today.replace(day=1) - timedelta(days=1)).replace(day=1)  # previous month logic
            # simpler: build month start by subtracting months
            from dateutil.relativedelta import relativedelta
            mstart = (today.replace(day=1) + relativedelta(months=-i))
            mend = (mstart + relativedelta(months=1)) - timedelta(days=1)
            labels.append(mstart.strftime("%b %Y"))
            agg = AddictionEntry.objects.filter(student=student, date__gte=mstart, date__lte=mend).aggregate(
                avg_mood=Avg("mood"), avg_craving=Avg("craving_level"))
            mood.append(agg["avg_mood"] or None)
            craving.append(agg["avg_craving"] or None)
            # recovery average compute approx
            recs = AddictionEntry.objects.filter(student=student, date__gte=mstart, date__lte=mend)
            if recs.exists():
                recovery.append(round(sum(r.recovery_score for r in recs)/recs.count(),1))
            else:
                recovery.append(None)
    else:
        return HttpResponseBadRequest("Invalid period")

    return JsonResponse({
        "labels": labels,
        "mood": mood,
        "craving": craving,
        "recovery": recovery,
    })
 
@login_required
def addiction_report_pdf(request):
    student = request.user.student
    logs = AddictionEntry.objects.filter(student=student)
    html = render_to_string("students/addiction_pdf.html", {"student": student, "logs": logs})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="recovery_report_{student.student_id}.pdf"'

    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    return response


@login_required
def student_notifications(request):
    student = request.user.student  # if user is logged in as student
    notifications = StudentNotification.objects.filter(student=student).order_by('-created_at')
    return render(request, "students/notifications.html", {"notifications": notifications})


 
 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Student, DailyBehavior, RiskPrediction
from .forms import StudentForm, DailyBehaviorForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import joblib
import json
import numpy as np
import tensorflow as tf
 
 
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

 

# # Load models once (for performance)
# scaler = joblib.load("models/scaler.joblib")
# with open("models/student_behavior_xgb.json", "r") as f:
#     xgb_model_json = json.load(f)
# # Example: If using XGBoost you can reload like this:
# # import xgboost as xgb
# # xgb_model = xgb.Booster()
# # xgb_model.load_model("models/student_behavior_xgb.json")

# lstm_model = tf.keras.models.load_model("models/student_behavior_lstm_supervised.h5")


# # @login_required
# # def student_dashboard(request):
# #     student = Student.objects.filter(student_id=request.user.username).first()

# #     latest_behavior = None
# #     latest_prediction = None

# #     if student:
# #         latest_behavior = DailyBehavior.objects.filter(student=student).order_by("-date").first()

# #         if latest_behavior:
# #             # Prepare input features
# #             features = np.array([[
# #                 latest_behavior.screen_time_hrs,
# #                 latest_behavior.night_usage_hrs,
# #                 latest_behavior.sleep_hours,
# #                 latest_behavior.app_social_hrs,
# #                 latest_behavior.app_entertainment_hrs,
# #                 latest_behavior.app_education_hrs,
# #                 int(latest_behavior.late_sleep_flag),
# #                 int(latest_behavior.low_sleep_flag),
# #             ]])

# #             # Scale
# #             features_scaled = scaler.transform(features)

# #             # Predict (example with LSTM)
# #             prediction = lstm_model.predict(features_scaled, verbose=0)
# #             risk_score = float(prediction[0][0])  # depends on model output
# #             risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

# #             # Save prediction in DB
# #             latest_prediction = RiskPrediction.objects.create(
# #                 student=student,
# #                 risk_label=risk_label,
# #                 risk_score=risk_score,
# #                 metadata={"model": "LSTM"}
# #             )

# #     return render(request, "students/dashboard.html", {
# #         "student": student,
# #         "latest_behavior": latest_behavior,
# #         "latest_prediction": latest_prediction,
# #     })
 

# def student_dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect("login")

#     # try to find student profile matching logged-in username
#     student = Student.objects.filter(student_id=request.user.username).first()

#     if not student:
#         return render(request, "students/dashboard.html", {
#             "error": "No student profile found for this user."
#         })

#     # load behaviors + predictions for that student
#     behaviors = student.behaviors.all().order_by("-date")[:10]
#     predictions = student.predictions.all().order_by("-timestamp")[:5]

#     return render(request, "students/dashboard.html", {
#         "student": student,
#         "behaviors": behaviors,
#         "predictions": predictions,
#     })

 
# Load models once
scaler = joblib.load("models/scaler.joblib")
lstm_model = tf.keras.models.load_model("models/student_behavior_lstm_supervised.h5")

# @login_required
# def student_dashboard(request):
#     # fetch the student profile linked to logged-in user
#     student = getattr(request.user, "student", None)

#     if not student:
#         return render(request, "students/dashboard.html", {
#             "error": "No student profile linked to this account."
#         })

#     latest_behavior = DailyBehavior.objects.filter(student=student).order_by("-date").first()
#     latest_prediction = None

#     if latest_behavior:
#         # prepare features
#         features = np.array([[
#             latest_behavior.screen_time_hrs,
#             latest_behavior.night_usage_hrs,
#             latest_behavior.sleep_hours,
#             latest_behavior.app_social_hrs,
#             latest_behavior.app_entertainment_hrs,
#             latest_behavior.app_education_hrs,
#             int(latest_behavior.late_sleep_flag),
#             int(latest_behavior.low_sleep_flag),
#         ]])

#         features_scaled = scaler.transform(features)

#         # predict with LSTM
#         prediction = lstm_model.predict(features_scaled, verbose=0)
#         risk_score = float(prediction[0][0])
#         risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

#         # save prediction
#         latest_prediction = RiskPrediction.objects.create(
#             student=student,
#             risk_label=risk_label,
#             risk_score=risk_score,
#             metadata={"model": "LSTM"}
#         )

#     return render(request, "students/dashboard.html", {
#         "student": student,
#         "latest_behavior": latest_behavior,
#         "latest_prediction": latest_prediction,
#     })

 
# @login_required
# def student_dashboard(request):
#     # ensure student profile exists
#     student, created = Student.objects.get_or_create(user=request.user)

#     latest_behavior = DailyBehavior.objects.filter(student=student).order_by("-date").first()
#     latest_prediction = None

#     if latest_behavior:
#         # prepare features
#         features = np.array([[ 
#             latest_behavior.screen_time_hrs,
#             latest_behavior.night_usage_hrs,
#             latest_behavior.sleep_hours,
#             latest_behavior.app_social_hrs,
#             latest_behavior.app_entertainment_hrs,
#             latest_behavior.app_education_hrs,
#             int(latest_behavior.late_sleep_flag),
#             int(latest_behavior.low_sleep_flag),
#         ]])

#         features_scaled = scaler.transform(features)

#         # predict with LSTM
#         prediction = lstm_model.predict(features_scaled, verbose=0)
#         risk_score = float(prediction[0][0])
#         risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

#         # save prediction
#         latest_prediction = RiskPrediction.objects.create(
#             student=student,
#             risk_label=risk_label,
#             risk_score=risk_score,
#             metadata={"model": "LSTM"}
#         )

#     return render(request, "students/dashboard.html", {
#         "student": student,
#         "latest_behavior": latest_behavior,
#         "latest_prediction": latest_prediction,
#         "created": created  # optional, to show “Profile created” message
#     })
# new
@login_required
def student_dashboard(request):
    student, created = Student.objects.get_or_create(user=request.user)

    latest_behavior = DailyBehavior.objects.filter(student=student).order_by("-date").first()
    latest_prediction = None
    behaviors = []
    predictions = []

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
    }

    return render(request, "students/dashboard.html", context)



@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("students/student_list")  # redirect to list page after saving
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form})
 
@login_required
def upload_behavior(request):
    if request.method == "POST":
        form = DailyBehaviorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("students/behavior_success.html")  # you can create a success page
    else:
        form = DailyBehaviorForm()
    return render(request, "students/behavior_form.html", {"form": form})
 
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

# @login_required
# def add_daily_behavior(request):
#     student, _ = Student.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         form = DailyBehaviorForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data

#             # ✅ Prevent duplicates
#             behavior, created = DailyBehavior.objects.update_or_create(
#                 student=student,
#                 date=data["date"],
#                 defaults={
#                     "screen_time_hrs": data["screen_time_hrs"],
#                     "night_usage_hrs": data["night_usage_hrs"],
#                     "sleep_hours": data["sleep_hours"],
#                     "app_social_hrs": data["app_social_hrs"],
#                     "app_entertainment_hrs": data["app_entertainment_hrs"],
#                     "app_education_hrs": data["app_education_hrs"],
#                     "late_sleep_flag": data["late_sleep_flag"],
#                     "low_sleep_flag": data["low_sleep_flag"],
#                 }
#             )

#             # ✅ fetch *all available days* (latest 7 max)
#             behaviors = DailyBehavior.objects.filter(student=student).order_by("-date")[:7]

#             if behaviors.exists():
#                 features = np.array([
#                     [
#                         b.screen_time_hrs,
#                         b.night_usage_hrs,
#                         b.sleep_hours,
#                         b.app_social_hrs,
#                         b.app_entertainment_hrs,
#                         b.app_education_hrs,
#                         int(b.late_sleep_flag),
#                         int(b.low_sleep_flag),
#                     ]
#                     for b in reversed(behaviors)  # oldest → newest
#                 ])

#                 # ✅ scale features
#                 features_scaled = scaler.transform(features)

#                 # ✅ reshape dynamically (batch, timesteps, features)
#                 features_reshaped = features_scaled.reshape((1, features_scaled.shape[0], features_scaled.shape[1]))

#                 # ✅ predict
#                 prediction = lstm_model.predict(features_reshaped, verbose=0)
#                 risk_score = float(prediction[0][0])
#                 risk_label = "High Risk" if risk_score > 0.6 else "Low Risk"

#                 # ✅ store prediction
#                 RiskPrediction.objects.create(
#                     student=student,
#                     risk_label=risk_label,
#                     risk_score=risk_score,
#                     metadata={"model": "LSTM", "days_used": features.shape[0]}
#                 )

#             return redirect('student_dashboard')

#     else:
#         form = DailyBehaviorForm()

#     return render(request, 'students/add_behavior.html', {'form': form})

import os
import xgboost as xgb
from tensorflow.keras.models import load_model
# # BASE_DIR → project root (where manage.py is)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Folder where all your models live
# MODEL_DIR = os.path.join(BASE_DIR, "models")  # <-- replace "models" with your folder name if different

# # Scaler & label encoder
# scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
# label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.joblib"))

# # LSTM models
# lstm_model = load_model(os.path.join(MODEL_DIR, "student_behavior_lstm_supervised.h5"))
# feature_extractor = load_model(os.path.join(MODEL_DIR, "student_behavior_feature_extractor.h5"))

# # XGBoost
# xgb_model = xgb.XGBClassifier()
# xgb_model.load_model(os.path.join(MODEL_DIR, "student_behavior_xgb.json"))


# # ----------------------
# # Utility
# # ----------------------
# def prepare_input(data, sequence_length=7, feature_count=8):
#     arr = np.array(data, dtype=float)
#     if arr.shape[0] < sequence_length:
#         padding = np.zeros((sequence_length - arr.shape[0], feature_count))
#         arr = np.vstack([padding, arr])
#     elif arr.shape[0] > sequence_length:
#         arr = arr[-sequence_length:]
#     return arr.reshape(1, sequence_length, feature_count)
 
# @login_required
# def add_daily_behavior(request):
#     student, _ = Student.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         form = DailyBehaviorForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data

#             # Save or update today's behavior
#             behavior, _ = DailyBehavior.objects.update_or_create(
#                 student=student,
#                 date=data["date"],
#                 defaults={
#                     "screen_time_hrs": data["screen_time_hrs"],
#                     "night_usage_hrs": data["night_usage_hrs"],
#                     "sleep_hours": data["sleep_hours"],
#                     "app_social_hrs": data["app_social_hrs"],
#                     "app_entertainment_hrs": data["app_entertainment_hrs"],
#                     "app_education_hrs": data["app_education_hrs"],
#                     "late_sleep_flag": data["late_sleep_flag"],
#                     "low_sleep_flag": data["low_sleep_flag"],
#                 }
#             )

#             # Fetch last 7 days of behaviors
#             behaviors = DailyBehavior.objects.filter(student=student).order_by("-date")[:7]

#             if behaviors.exists():
#                 features = np.array([
#                     [
#                         b.screen_time_hrs,
#                         b.night_usage_hrs,
#                         b.sleep_hours,
#                         b.app_social_hrs,
#                         b.app_entertainment_hrs,
#                         b.app_education_hrs,
#                         int(b.late_sleep_flag),
#                         int(b.low_sleep_flag),
#                     ]
#                     for b in reversed(behaviors)
#                 ])

#                 # Scale features
#                 features_scaled = scaler.transform(features)

#                 # Pad/truncate for LSTM
#                 X_input = prepare_input(features_scaled, sequence_length=7, feature_count=features_scaled.shape[1])

#                 # Extract features from LSTM
#                 lstm_features = feature_extractor.predict(X_input, verbose=0)

#                 # XGBoost prediction
#                 y_pred = xgb_model.predict(lstm_features)[0]
#                 y_proba = xgb_model.predict_proba(lstm_features)[0]
#                 risk_label = label_encoder.inverse_transform([y_pred])[0]

#                 # Save prediction
#                 RiskPrediction.objects.create(
#                     student=student,
#                     risk_label=risk_label,
#                     risk_score=float(np.max(y_proba)),
#                     metadata={
#                         "model": "LSTM+XGBoost",
#                         "days_used": features.shape[0],
#                         "probabilities": y_proba.tolist()
#                     }
#                 )

#             return redirect('student_dashboard')

#     else:
#         form = DailyBehaviorForm()

#     return render(request, 'students/add_behavior.html', {'form': form})

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
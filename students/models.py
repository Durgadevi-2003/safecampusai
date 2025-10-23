from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,related_name="student")
    student_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class DailyBehavior(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behaviors")
    date = models.DateField()
    screen_time_hrs = models.FloatField()
    night_usage_hrs = models.FloatField()
    sleep_hours = models.FloatField()
    app_social_hrs = models.FloatField()
    app_entertainment_hrs = models.FloatField()
    app_education_hrs = models.FloatField()
    late_sleep_flag = models.BooleanField(default=False)
    low_sleep_flag = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "date")
        indexes = [models.Index(fields=["student", "date"])]

class RiskPrediction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="predictions")
    timestamp = models.DateTimeField(auto_now_add=True)
    risk_label = models.CharField(max_length=50)
    risk_score = models.FloatField()
    metadata = models.JSONField(null=True, blank=True)
 
class AddictionEntry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="addiction_entries")
    date = models.DateField(default=timezone.localdate)
    mood = models.PositiveSmallIntegerField(help_text="1 (very low) - 10 (very good)")
    craving_level = models.PositiveSmallIntegerField(help_text="1 (no craving) - 10 (very strong)")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student.student_id} - {self.date} (mood {self.mood}, craving {self.craving_level})"

    @property
    def recovery_score(self):
        # Simple recovery metric: higher mood and lower craving => higher score
        # Normalize to 0-100
        score = (self.mood * 10) * (1 - (self.craving_level - 1) / 9)  # heuristic
        return round(score, 1)

class DrugAlert(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="drug_alerts")
    text = models.TextField()
    label = models.CharField(max_length=50)
    score = models.FloatField()
    detected_words = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.label} ({self.score}%)"

class StudentNotification(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.student.name or self.student.user.username}"


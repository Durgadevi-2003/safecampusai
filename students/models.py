from django.db import models
from django.contrib.auth.models import User
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,related_name="student")
    student_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.student_id

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

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User
from students.models import Student

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username
 
class CounselingSession(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counseling_sessions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_sessions")
    session_date = models.DateTimeField(default=timezone.now)
    mode = models.CharField(
        max_length=20,
        choices=[
            ("In-person", "In-person"),
            ("Video Call", "Video Call"),
            ("Phone Call", "Phone Call")
        ],
        default="In-person"
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Scheduled", "Scheduled"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        default="Scheduled"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.mode} ({self.status})"




from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student 
from .models import DailyBehavior, RiskPrediction
import random

@receiver(post_save, sender=DailyBehavior)
def create_risk_prediction(sender, instance, created, **kwargs):
    if created:
        # Example: basic logic (replace with your ML model later)
        score = random.uniform(0.8, 1.0)
        label = "High Risk" if score > 0.9 else "Medium Risk"

        # Save prediction for that student
        RiskPrediction.objects.create(
            student=instance.student,
            risk_label=label,
            risk_score=score
        )

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
     if created:
        Student.objects.create(
            user=instance,
            student_id=instance.username,   # use username as student_id
            name=instance.username,         # default name
            email=instance.email or ""      # copy email
        )
@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if hasattr(instance, 'student'):
        instance.student.save()

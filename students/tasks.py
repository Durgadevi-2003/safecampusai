from celery import shared_task
from .models import Student, DailyBehavior, RiskPrediction
from .utils.predictor import predict_for_student_behaviors, SEQ_LEN
from django.core.mail import send_mail

@shared_task
def daily_all_students_predict():
    for student in Student.objects.all():
        behaviors = list(DailyBehavior.objects.filter(student=student).order_by("-date")[:SEQ_LEN])
        behaviors = list(reversed(behaviors))
        res = predict_for_student_behaviors(behaviors)
        if res:
            RiskPrediction.objects.create(student=student, risk_label=res["label"], risk_score=res["score"], metadata={"probs": res["probs"]})
            if res["score"] > 0.75:
                if student.email:
                    send_mail(
                        subject=f"Risk Alert: {res['label']}",
                        message=f"Dear {student.name}, risk score {res['score']:.2f}",
                        from_email="noreply@tracker.com",
                        recipient_list=[student.email],
                    )

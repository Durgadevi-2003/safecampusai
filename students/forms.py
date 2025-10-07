from django import forms
from .models import Student, DailyBehavior

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_id", "name", "email"]
        widgets = {
            "student_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Student ID"
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Full Name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),
        }

class DailyBehaviorForm(forms.ModelForm):
    class Meta:
        model = DailyBehavior
        fields = [
            "student",
            "date",
            "screen_time_hrs",
            "night_usage_hrs",
            "sleep_hours",
            "app_social_hrs",
            "app_entertainment_hrs",
            "app_education_hrs",
            "late_sleep_flag",
            "low_sleep_flag",
        ]
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "screen_time_hrs": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter screen time in hours"
            }),
            "night_usage_hrs": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter night usage in hours"
            }),
            "sleep_hours": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter sleep hours"
            }),
            "app_social_hrs": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Social media usage in hours"
            }),
            "app_entertainment_hrs": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Entertainment app usage in hours"
            }),
            "app_education_hrs": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Education app usage in hours"
            }),
            "late_sleep_flag": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "low_sleep_flag": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

 
 
 
 
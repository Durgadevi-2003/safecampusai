from rest_framework import serializers
from .models import Student, DailyBehavior, RiskPrediction

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class DailyBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyBehavior
        fields = "__all__"

class RiskPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskPrediction
        fields = "__all__"

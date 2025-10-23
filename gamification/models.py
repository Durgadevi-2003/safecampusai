from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="streak")
    last_login_date = models.DateField(null=True, blank=True)
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)

    def update_streak(self):
        today = date.today()
        if self.last_login_date == today:
            return  # already counted today
        elif self.last_login_date == today.replace(day=today.day - 1):
            self.current_streak += 1
        else:
            self.current_streak = 1  # reset
        self.last_login_date = today
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
        self.save()

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, default="🌟")

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="leaderboard_entry")
    points = models.IntegerField(default=0)

    def add_points(self, value):
        self.points += value
        self.save()

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Leaderboard

@login_required
def leaderboard_view(request):
    top_users = Leaderboard.objects.order_by("-points")[:10]
    return render(request, "gamification/leaderboard.html", {"top_users": top_users})

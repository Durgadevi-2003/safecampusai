def unread_notifications(request):
    if request.user.is_authenticated and hasattr(request.user, 'student'):
        return {
            'unread_count': request.user.student.notifications.filter(read=False).count()
        }
    return {'unread_count': 0}

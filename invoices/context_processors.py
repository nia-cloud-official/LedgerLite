from .models import Notification

def notifications_context(request):

    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            read=False
        ).count()

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

    else:
        unread_notifications_count = 0
        notifications = []

    return {
        "unread_notifications_count": unread_notifications_count,
        "notifications": notifications
    }
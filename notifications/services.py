from .models import Notification

def send_notification(recipient, title, message, link=None, notification_type='INFO'):
    """
    Helper function to create a notification for a user.
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        link=link,
        notification_type=notification_type
    )

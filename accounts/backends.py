from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Allows authentication with either email address or username.
    Works seamlessly with client.login(username=...) and client.login(email=...).
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        login_id = email or username or kwargs.get(User.USERNAME_FIELD)
        if not login_id:
            return None
        
        try:
            user = User.objects.filter(
                Q(email__iexact=login_id) | Q(username__iexact=login_id)
            ).first()
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None
        return None

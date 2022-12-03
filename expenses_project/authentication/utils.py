from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import AbstractBaseUser

class AppTokenGenerator(PasswordResetTokenGenerator):

    # more on making hash value at: https://github.com/django/django/blob/main/django/contrib/auth/tokens.py#L8
    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        return str(user.is_active)+str(user.pk)+str(timestamp)

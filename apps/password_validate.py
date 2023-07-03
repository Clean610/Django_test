from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        upper_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lower_characters = "abcdefghijklmnopqrstuvwxyz"
        if len(password) < self.min_length:
            raise ValidationError(_('Your password must be at least 8 characters long.'))
        if not any(char.isdigit() for char in password):
            raise ValidationError(_('Your password must contain at least one number digit.'))
        if not any(char.isalpha() for char in password):
            raise ValidationError(_('Your password must contain at least one character.'))
        if not any(char in upper_characters for char in password):
            raise ValidationError(_('Your Password must be contain at least one uppercase and one lowercase.'))
        if not any(char in lower_characters for char in password):
            raise ValidationError(_('Your Password must be contain at least one uppercase and one lowercase.'))
        if not any(char in special_characters for char in password):
            raise ValidationError(_('Your password must contin at least one special character.'))

    @staticmethod
    def get_help_text():
        return ""

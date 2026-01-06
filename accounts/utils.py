import random
import string
from django.core import signing

CAPTCHA_SALT = "pump-login-captcha"

def generate_captcha():
    """Generate random captcha text like ABC7."""
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digit = str(random.randint(1, 9))
    return letters + digit


def sign_captcha(value):
    return signing.dumps(value, salt=CAPTCHA_SALT)


def read_captcha(token):
    return signing.loads(token, salt=CAPTCHA_SALT)

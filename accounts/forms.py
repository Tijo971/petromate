from django import forms
from .models import *

import random
import string
from django import forms
from django.core import signing
from django.core.exceptions import ValidationError

# Required constant
_CAPTCHA_SIGNING_SALT = "pump_login_captcha_salt"

import random
import string

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError

# optional: choose a salt unique to this form
_CAPTCHA_SIGNING_SALT = "petrol_pump_captcha_v1"


class PetrolPumpWithCouponForm(forms.ModelForm):
    """
    This form creates BOTH:
    - PetrolPump
    - CouponCode (linked to the pump)

    Added: a combined text+number captcha (e.g. "ABZ4").
    """

    # Extra fields from CouponCode model
    coupon_code = forms.CharField(
        required=False,  # <-- make it optional
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter coupon code"
        })
    )

    is_used = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input"
        })
    )

    # Captcha fields
    captcha = forms.CharField(
        required=True,
        max_length=10,
        label="Captcha",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter the characters shown"
        }),
       
    )

    # hidden signed token holding expected captcha answer
    captcha_token = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = PetrolPump
        fields = [
            "petrol_pump_name",
            "licensee_name",
            "licence_number",
            "email",
            "mobile_number",
        ]

        widgets = {
            "petrol_pump_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter petrol pump name"
            }),
            "licensee_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter licensee name"
            }),
            "licence_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter licence number"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email"
            }),
            "mobile_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter mobile number"
            }),
        }

    # ----------------------
    # VALIDATION METHODS
    # ----------------------

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        if mobile and (len(mobile) < 10 or len(mobile) > 15):
            raise forms.ValidationError("Mobile number must be 10–15 digits.")
        return mobile

    def clean_licence_number(self):
        licence = self.cleaned_data.get("licence_number")
        if " " in licence:
            raise forms.ValidationError("Licence number must not contain spaces.")
        return licence

    def clean_coupon_code(self):
        coupon = self.cleaned_data.get("coupon_code")

        if not coupon:
            return ""   # Allow empty coupon

        if " " in coupon:
            raise forms.ValidationError("Coupon code cannot contain spaces.")

        if len(coupon) < 4:
            raise forms.ValidationError("Coupon code must be at least 4 characters.")

        return coupon

    def clean_captcha(self):
        """
        Verify user-entered captcha against signed token.
        Comparison is case-insensitive.
        """
        user_input = self.cleaned_data.get("captcha", "").strip()
        token = self.data.get("captcha_token") or self.cleaned_data.get("captcha_token")

        if not token:
            raise ValidationError("Captcha verification failed (missing token). Please reload the page and try again.")

        try:
            expected = signing.loads(token, salt=_CAPTCHA_SIGNING_SALT)
        except signing.BadSignature:
            raise ValidationError("Captcha verification failed (invalid token). Please reload the page and try again.")

        if not user_input:
            raise ValidationError("Please enter the captcha shown.")

        # case-insensitive compare
        if user_input.lower() != str(expected).lower():
            raise ValidationError("Captcha does not match.")

        # If verification passes, return normalized value (not really used further)
        return user_input

    def clean(self):
        cleaned_data = super().clean()
        # duplicate coupon check will be done AFTER pump creation
        return cleaned_data

    # -------------------------------------
    # SAVE METHOD (CREATES BOTH RECORDS)
    # -------------------------------------
    def save(self, commit=True):
        pump = super().save(commit=True)

        coupon = self.cleaned_data.get("coupon_code")

        # Create coupon ONLY IF user entered something
        if coupon:
            CouponCode.objects.create(
                petrol_pump=pump,
                coupon_code=coupon,
                is_used=self.cleaned_data.get("is_used", False),
            )

        return pump

    # ---------------------
    # CAPTCHA: generation & helper
    # ---------------------
    def _generate_challenge(self, letters=3, digits=1):
        """Return a string like 'ABC7'."""
        letters_part = "".join(random.choices(string.ascii_uppercase, k=letters))
        digits_part = "".join(str(random.randint(0, 9)) for _ in range(digits))
        return f"{letters_part}{digits_part}"

    def __init__(self, *args, **kwargs):
        """
        On initial (unbound) rendering, generate a random captcha challenge,
        sign it, and put the signed token into captcha_token initial value.

        On bound forms (POST), recover the challenge from the provided token
        so it can be displayed again (we set self.captcha_challenge for templates).
        """
        super().__init__(*args, **kwargs)

        self.captcha_challenge = None  # string shown to user (e.g. "ABC7")

        # If form is bound (POST), try to recover challenge from incoming token so
        # templates can show the same challenge after form validation errors.
        if self.is_bound:
            token = (self.data.get("captcha_token") or self.initial.get("captcha_token"))
            if token:
                try:
                    self.captcha_challenge = signing.loads(token, salt=_CAPTCHA_SIGNING_SALT)
                except signing.BadSignature:
                    # leave captcha_challenge None; clean_captcha will raise a validation error
                    self.captcha_challenge = None
        else:
            # unbound form: generate a fresh challenge and set the hidden token initial
            challenge = self._generate_challenge(letters=3, digits=1)  # e.g. "KTY4"
            token = signing.dumps(challenge, salt=_CAPTCHA_SIGNING_SALT)
            # set the hidden token initial so it will render into the form
            self.fields["captcha_token"].initial = token
            # also expose the human-readable challenge for templates
            self.captcha_challenge = challenge





# Login forms.py




from django import forms

class PetrolPumpLoginForm(forms.Form):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
            "id": "id_username",  # MUST match JS selector
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "id": "id_password",
        })
    )

    captcha_challenge = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "readonly": True,
            "class": "captcha-box",
            "id": "id_captcha_challenge"
        })
    )

    captcha = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Captcha",
            "id": "id_captcha"
        })
    )

    captcha_token = forms.CharField(widget=forms.HiddenInput())

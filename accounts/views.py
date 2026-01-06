from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.http import JsonResponse
from .models import*
from django.utils import timezone
from .forms import*
import random
import requests 
from .utils import generate_captcha, sign_captcha, read_captcha

# Create your views here.




class LoginView(TemplateView):
    template_name = "accounts/login.html"







class PetrolPumpRegisterView(CreateView):
    model = PetrolPump
    form_class = PetrolPumpWithCouponForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:otp-verify")

    def get_form(self, form_class=None):
        """
        Keep a reference to the form instance so we can expose the captcha challenge
        to the template via get_context_data.
        """
        form = super().get_form(form_class)
        self._form_instance = form
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # -------------------------------
        # STORE IP IN SESSION (HIDDEN)
        # -------------------------------
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            user_ip = x_forwarded_for.split(",")[0]
        else:
            user_ip = self.request.META.get("REMOTE_ADDR")

        self.request.session["user_ip"] = user_ip
        # (NOT adding context["user_ip"] so it stays hidden)

        # expose captcha challenge
        form_instance = getattr(self, "_form_instance", None)
        if form_instance is not None:
            context["captcha_challenge"] = getattr(form_instance, "captcha_challenge", None)

        return context

    def form_valid(self, form):
        pump = form.save(commit=False)

        # capture IP (already stored in session, but keeping your original behavior)
        pump.ip_address = self.request.META.get("REMOTE_ADDR")
        pump.is_active = False
        pump.save()

        # ----------------------------------------
        # NEW: Mark coupon code as used
        # ----------------------------------------
        coupon_code = form.cleaned_data.get("coupon_code")

        if coupon_code:
            try:
                coupon = CouponCode.objects.get(coupon_code=coupon_code, is_used=False)
                coupon.is_used = True
                coupon.used_by = pump
                coupon.save()
            except CouponCode.DoesNotExist:
                messages.error(self.request, "Invalid or already used coupon code.")
                return redirect("accounts:register")

        # generate token
        token = get_random_string(50)
        pump.email_activation_token = token
        pump.save()

        activation_link = self.request.build_absolute_uri(
            reverse("accounts:activate-account") + f"?token={token}"
        )

        subject = "Activate your Petrol Pump Account"
        message = f"""
        Dear {pump.petrol_pump_name},

        Click the link below to activate your account:
        {activation_link}

        Thank you,
        Petromate Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [pump.email],
            fail_silently=False,
        )

        messages.success(self.request, "Registration successful! Check your email for activation link.")
        return redirect("accounts:register")
# ===================================================================
# 2. EMAIL ACTIVATION VIEW – SEND OTP TO MOBILE
# ===================================================================
class ActivateAccountView(View):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return HttpResponseForbidden("Invalid activation link!")

        try:
            pump = PetrolPump.objects.get(email_activation_token=token)
        except PetrolPump.DoesNotExist:
            return HttpResponseForbidden("Invalid or expired activation link!")

        # Generate OTP
        otp = random.randint(100000, 999999)
        pump.mobile_otp = otp
        pump.save()

        message = (
            f"Hi Sir, Welcome to PETROMATE. Your Verification Code is {otp}. "
            f"Pls contact customer care for any support. Thanks."
        )

        print(f"Sending OTP to {pump.mobile_number}: {otp}")

        url = (
            "http://sms.moplet.com/api/sendhttp.php?"
            f"authkey=597AI8vDDMfDy5a49da10"
            f"&mobiles={pump.mobile_number}"
            f"&message={message}"
            f"&sender=GEOSYS&route=4&country=91"
            f"&DLT_TE_ID=1207161725928772868"
        )

        try:
            response = requests.get(url)
            if response.status_code != 200:
                return JsonResponse(
                    {"error": "Failed to send OTP", "details": response.text},
                    status=500
                )
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": "Moplet request failed", "details": str(e)},
                status=500
            )
        messages.success(request, "Email verified! OTP sent to your mobile.")
        request.session["pump_id"] = pump.id
        return redirect("accounts:otp-verify")


# ===================================================================
# 3. OTP VERIFICATION VIEW
# ===================================================================
class OTPVerifyView(View):
    template_name = "accounts/otp_verify.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        entered_otp = request.POST.get("otp")

        try:
            pump = PetrolPump.objects.get(mobile_otp=entered_otp)
        except PetrolPump.DoesNotExist:
            messages.error(request, "Invalid OTP!")
            return redirect("accounts:otp-verify")

        # Store pump ID in session for next step (password creation)
        request.session["pump_id"] = pump.id

        return redirect("accounts:set-password")


class SetPasswordView(View):
    template_name = "accounts/setpassword.html"

    def get(self, request):
        pump_id = request.session.get("pump_id")

        if not pump_id:
            messages.error(request, "Session expired. Please verify OTP again.")
            return redirect("accounts:otp-verify")

        pump = PetrolPump.objects.get(id=pump_id)
        return render(request, self.template_name, {"email": pump.email})

    def post(self, request):
        from django.utils import timezone

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        pump_id = request.session.get("pump_id")

        if not pump_id:
            messages.error(request, "Session expired. Please verify OTP again.")
            return redirect("accounts:otp-verify")

        pump = PetrolPump.objects.get(id=pump_id)

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("accounts:set-password")

        # Activate parent model
        pump.is_active = True
        pump.mobile_otp = None
        pump.email_activation_token = None
        pump.save()

        # Create or update login account
        login_obj, created = PetrolPumpLogin.objects.get_or_create(
            pump=pump,
            defaults={
                "username": pump.email,
                "pump_name": pump.petrol_pump_name,   # Set pump name here
            }
        )

        # Update login details
        login_obj.username = pump.email
        login_obj.pump_name = pump.petrol_pump_name   # Save pump name
        login_obj.set_password(password)

        # Save IP address from middleware
        login_obj.last_login_ip = getattr(request, "user_ip", None)
        login_obj.last_login_at = timezone.now()
        login_obj.save()

        # Remove session
        if "pump_id" in request.session:
            del request.session["pump_id"]

        messages.success(request, "Password set successfully! You can now login.")
        return redirect("accounts:login")


class ResendOTPView(View):
    def get(self, request):
        pump_id = request.session.get("pump_id")

        if not pump_id:
            return JsonResponse({"error": "No user session found!"}, status=400)

        try:
            pump = PetrolPump.objects.get(id=pump_id)
        except PetrolPump.DoesNotExist:
            return JsonResponse({"error": "Petrol pump not found!"}, status=404)

        # Generate new OTP
        otp = random.randint(100000, 999999)
        pump.mobile_otp = otp
        pump.save()

        message = (
            f"Hi Sir, Welcome to PETROMATE. Your Verification Code is {otp}. "
            f"Pls contact customer care for any support. Thanks."
        )

        print(f"RESENDING OTP to {pump.mobile_number}: {otp}")

        url = (
            "http://sms.moplet.com/api/sendhttp.php?"
            f"authkey=597AI8vDDMfDy5a49da10"
            f"&mobiles={pump.mobile_number}"
            f"&message={message}"
            f"&sender=GEOSYS&route=4&country=91"
            f"&DLT_TE_ID=1207161725928772868"
        )

        try:
            response = requests.get(url)
            if response.status_code != 200:
                return JsonResponse(
                    {"error": "Failed to resend OTP", "details": response.text},
                    status=500
                )
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": "Resend request failed", "details": str(e)},
                status=500
            )

        return JsonResponse({"message": "OTP Resent Successfully"}, status=200)
    



from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import PetrolPump, PetrolPumpLogin
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
import random
import string
from django.db.models import Q

# Helper to generate a new captcha
def generate_captcha(length=6):
    """
    Generate a random alphanumeric captcha of given length.
    Returns:
        captcha_text (str): the text user must enter
    """
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    captcha_text = ''.join(random.choices(characters, k=length))
    return captcha_text

class PetrolPumpLoginView(View):
    def get(self, request):
        # Generate captcha
        captcha_text = generate_captcha()
        request.session['captcha_text'] = captcha_text  # store in session

        return render(request, "accounts/login.html", {
            "captcha_text": captcha_text
        })

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        captcha_value = request.POST.get("captcha", "").strip()
        session_captcha = request.session.get("captcha_text")

        error = None

        # -----------------------
        # Validate captcha
        # -----------------------
        if not captcha_value:
            error = "Captcha is required"
        elif session_captcha is None or captcha_value.upper() != session_captcha:
            error = "Invalid captcha"

        # -----------------------
        # Validate username/password
        # -----------------------
        if not error:
            try:
                login_obj = PetrolPumpLogin.objects.get(username=username)
                from django.contrib.auth.hashers import check_password
                if not check_password(password, login_obj.password):
                    error = "Invalid password"
            except PetrolPumpLogin.DoesNotExist:
                error = "Invalid username"

        # -----------------------
        # Handle errors or success
        # -----------------------
        if error:
            # Regenerate captcha for retry
            captcha_text = generate_captcha()
            request.session['captcha_text'] = captcha_text
            return render(request, "accounts/login.html", {
                "error": error,
                "captcha_text": captcha_text,
                "username": username
            })

        # Success → redirect
        return redirect("masters:dashboard")


from django.http import JsonResponse
from .models import PetrolPump, PetrolPumpLogin

def get_pump_name(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'error': 'Username is required'}, status=400)

    try:
        login_obj = PetrolPumpLogin.objects.get(username=username)
        pump_obj = login_obj.pump
        return JsonResponse({'pump_name': pump_obj.petrol_pump_name})
    except PetrolPumpLogin.DoesNotExist:
        return JsonResponse({'error': 'Invalid username'}, status=404)



class LogoutView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return redirect('accounts:login')

class ForgotPasswordView(TemplateView):
    template_name = "accounts/forgotpassword.html"

from django.urls import path


from accounts.views import *

from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', PetrolPumpLoginView.as_view(), name='login'),
    # path('forgotpassword/', ForgotPasswordView.as_view(), name='forgotpassword'),
    path("register/", PetrolPumpRegisterView.as_view(), name="register"),
    path("activate-account/", ActivateAccountView.as_view(), name="activate-account"),
    path("otp-verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("set-password/", SetPasswordView.as_view(), name="set-password"),
    path('get-pump-name/', get_pump_name, name='get_pump_name'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
]
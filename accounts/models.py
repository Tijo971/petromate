from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, Permission, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser

# class UserManager(BaseUserManager):
#     def create_user(self, username, password, **extra_fields):
#         """
#         Creates and saves a User with the given phone number and mpin.
#         """
#         if not username:
#             raise ValueError("The Username must be set")
#         if not password:
#             raise ValueError("Password must be set")
        
#         user = self.model(username=username, password=password, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_users(self, username,password, **extra_fields):
#         """
#         Creates and saves a superuser with the given phone number and mpin.
#         """
#         extra_fields.setdefault('is_pump', True)
#         extra_fields.setdefault('is_customer', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_pump') is not True:
#             raise ValueError("Superuser must have is_pump=True.")
#         if extra_fields.get('is_customer') is not True:
#             raise ValueError("Superuser must have is_superuser=True.")
        
#         return self.create_user(username, password, **extra_fields)


class PetrolPump(models.Model):
    petrol_pump_name = models.CharField(
        max_length=200,
        verbose_name="Petrol Pump Name"
    )

    licensee_name = models.CharField(
        max_length=200,
        verbose_name="Licensee Name"
    )

    licence_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Licence Number"
    )

    email = models.EmailField(
        max_length=150,
        validators=[EmailValidator()],
        verbose_name="Email",
        unique=True
    )

    mobile_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{10,15}$',
                message="Enter a valid mobile number"
            )
        ],
        verbose_name="Mobile Number"
    )
    email_activation_token = models.CharField(max_length=100, null=True, blank=True)
    mobile_otp = models.CharField(max_length=6, null=True, blank=True)



    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        null=True,
        blank=True,
        verbose_name="IP Address"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Petrol Pump"
        verbose_name_plural = "Petrol Pumps"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.petrol_pump_name} ({self.licence_number})"
    
    def set_password(self, raw_password):
        
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password."""
        return check_password(raw_password, self.password)



class CouponCode(models.Model):
    petrol_pump = models.ForeignKey(
        PetrolPump,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name="Petrol Pump"
    )

    coupon_code = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Coupon Code"
    )

    is_used = models.BooleanField(default=False)
    verified_on = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon Code"
        verbose_name_plural = "Coupon Codes"
        unique_together = ("petrol_pump", "coupon_code")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.coupon_code} - {self.petrol_pump.petrol_pump_name}"



class PetrolPumpLogin(models.Model):

    pump = models.ForeignKey(
        PetrolPump,
        on_delete=models.CASCADE,
        related_name="login_account"
    )

    pump_name = models.CharField(max_length=200, blank=True, null=True)

    username = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Last Login IP"
    )

    last_login_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"Login Account for {self.pump.petrol_pump_name}"
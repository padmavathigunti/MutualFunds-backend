from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from mutualfund_project import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class FundHouse(models.Model):
    name = models.CharField(max_length=255, unique=True) 

    def __str__(self):
        return self.name


class Scheme(models.Model):
    fund_house = models.ForeignKey(FundHouse, on_delete=models.CASCADE)
    scheme_code = models.IntegerField(unique=True)
    scheme_name = models.CharField(max_length=255)
    scheme_type = models.CharField(max_length=100)  
    scheme_category = models.CharField(max_length=100) 
    isin_growth = models.CharField(max_length=20, blank=True, null=True) 
    isin_reinvestment = models.CharField(max_length=20, blank=True, null=True) 
    is_open_ended = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.scheme_name} ({self.scheme_code})"


class NAV(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    date = models.DateField()  
    nav = models.FloatField()  

    class Meta:
        unique_together = ('scheme', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.scheme.scheme_name} - {self.date} - {self.nav}"



class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    units = models.FloatField()
    current_nav = models.FloatField(default=0.0)
    current_value = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_current_value(self):
        self.current_value = self.units * self.current_nav
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.scheme.scheme_name}"

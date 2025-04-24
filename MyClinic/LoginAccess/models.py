from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
import string
import random
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.crypto import get_random_string


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,mobile_number, password=None,password2=None,**extra_fields):
        """
        Creates and saves a User with the given user_name and password.
        """
        if not mobile_number:
            raise ValueError("Users must have an mobile_number")
        user = self.model(
            mobile_number=mobile_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,mobile_number, password=None,**extra_fields):
        """
        Creates and saves a User with the given user_name and password.
        """
        extra_fields.setdefault('is_admin', True)  # **Change**: Set is_admin to True by default
        extra_fields.setdefault('is_active', True)
        user = self.create_user(
            mobile_number=mobile_number,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

def generate_customer_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
  
class User(AbstractBaseUser):
    ROLE_CHOICES=(
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('lab', 'Lab'),
        ('ambulance', 'Ambulance'),
    )
    user_id = models.CharField(max_length=4, primary_key=True, default=generate_customer_id, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=20,unique=True)
    role = models.CharField(max_length=100,choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    firebase_registration_token = models.TextField(blank=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.mobile_number

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
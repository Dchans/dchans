from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.core.files.storage import default_storage
import base64
from cryptography.fernet import Fernet
import random
import string
import json
from io import BytesIO
class MyUserManager(BaseUserManager):
    def create_user(self,name,password=None,password2=None):
        if not name:
            raise ValueError("Users must have a Name")
        fernet=Fernet(User.generate_fernetkey(password))
        user = self.model(name=name,db_password=fernet.encrypt(''.join(random.choice(string.ascii_lowercase) for i in range(7)).encode()).decode())
        user.set_password(password)
        user.save(using=self._db)
        subscription.objects.create(user=user,app_type=0).save()
        default_storage.save(f"{user.id}\\config.bs",BytesIO(fernet.encrypt(json.dumps([]).encode())))
        return user
    def create_superuser(self,name,email,password=None):
        user = self.create_user(password=password,name=name)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email Address",max_length=255)
    name=models.CharField(max_length=200,unique=True)
    phone=models.CharField(verbose_name="Phone Number",max_length=15,default=None,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects = MyUserManager()
    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = ["email"]
    profile_pic = models.ImageField(default="male.png", null=True, blank=True)
    storage_size=models.FloatField(default=5)
    db_password=models.TextField()

    otp_limit=models.IntegerField(default=6)
    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
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
    @staticmethod
    def generate_fernetkey(password):
        salt = password.encode()
        kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
        backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(salt)).decode()
APP_CHOICES = [("0", 'Busyness'),]

class subscription(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    app_type=models.CharField(max_length=1, choices=APP_CHOICES)
    active=models.BooleanField(default=False)
    date_created=models.DateTimeField(auto_now_add=True)
    shop_name=models.CharField(max_length=200)
    address=models.CharField(max_length=200,default=" ", null=False, blank=False)
    def __str__(self):
        return self.user.name
V_CHOICES = [("0", 'Phone'),("1","Email")]


  


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
# from helpdesk.customadmin.models import Company


class CustomUser(AbstractUser):
    status_choice=(
        ('watting','Watting'),
        ('approved','Approved'),
        ('rejected','Rejected')
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    # is_landload = models.BooleanField(default=0)
    status = models.CharField(choices=status_choice,max_length=100,default='watting')
    delete_status = models.BooleanField(default=0)
    # strpass = models.CharField(max_length=255)
    token = models.CharField(max_length=16)
    # company=models.ForeignKey(Company,on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=10,null=True,blank=True)
    image = models.ImageField(upload_to='user_profile/', null=True,blank=True)
    address = models.CharField(max_length=500,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    zipcode = models.CharField(max_length=8,null=True,blank=True)
    country = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()


class ForgetPassMailVerify(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    link=models.CharField(max_length=500)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user

class UserEmailVerify(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    link = models.CharField(max_length=500)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user
    
class UserNumberVerify(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user
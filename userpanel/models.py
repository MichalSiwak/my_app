from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_picture = models.ImageField(null=True, upload_to='media/', default='/profile_image.png')
    is_email_verified = models.BooleanField(default=False)

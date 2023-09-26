from django.db import models
from django.contrib.auth.models import User
from base.models import Basemodel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.eamils import send_account_activation_email



class Profile(Basemodel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='ProfileImages', default='ProfileImages/default_pp.jpg')

    def __str__(self):
        return self.user.first_name

@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user=instance, email_token=email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
    
    except Exception as e:
        print(e)
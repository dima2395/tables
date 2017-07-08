from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from tables.models import Company

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_owner = models.BooleanField(default=False)
    #company


    # used to get companies list in main sidebar
    def get_companies(self):
      user = self.user
      if user.profile.is_owner:
        return user.company_set.all()
      else:
        return Company.objects.filter(employees=user)

    def __str__(self):
        return "{}'s profile".format(self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

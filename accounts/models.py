from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from tables.models import Company

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_owner = models.BooleanField(default=False)
    telephone_number = models.CharField(max_length=25, verbose_name='Номер телефона')
    EMPLOYEE_POSITIONS = (
    ('Manager', 'Менеджер'),
    ('Agent', 'Агент по продажам')
    )
    position = models.CharField(max_length=20, choices=EMPLOYEE_POSITIONS, default='Agent', verbose_name='Должность')


    # used to get companies list in main sidebar
    def get_companies(self):
      user = self.user
      if user.profile.is_owner:
        return user.company_set.all()
      else:
        return Company.objects.filter(employees=user)

    def in_company(self, company_pk):
        company = Company.objects.get(pk=company_pk)
        user = self.user
        if user == company.owner or (user in company.employees.all()):
            return True
        else:
            return False

    def is_manager(self):
        return self.position == 'Manager'

    def is_agent(self):
        return self.position == 'Agent'


    def __str__(self):
        return "{}'s profile".format(self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

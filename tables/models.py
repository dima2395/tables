from django.db import models
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    legal_address = models.CharField(max_length=128, blank=True, verbose_name='Юридический адрес')
    actual_address = models.CharField(max_length=128, blank=True, verbose_name='Фактический адрес')
    telephone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    email = models.EmailField(blank=True, verbose_name='Email')
    website = models.URLField(blank=True, verbose_name='Вебсайт')
    description = models.TextField(blank=True, verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    employees = models.ManyToManyField(User, related_name='employees')

    def __str__(self):
        return '{}\'s {}'.format(self.owner.username, self.name)

    def get_absolute_url(self):
        return reverse('tables:company-edit', kwargs={'pk': self.pk})


class Warehouse(models.Model):
    name = models.CharField(max_length=60, verbose_name='Название')
    address = models.CharField(max_length=128, blank=True, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    #owner_id   ForeighKey to user
    #employees   (OneToMany or ManyToMany) to user
    #created_at   datetime
    #last_modified   datetime
    def __str__(self):
        return '{}\'s {}'.format(self.company.owner.username, self.name)

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")
    barcode = models.CharField(max_length=128, blank=True, default="", verbose_name="Штрихкод")
    vendor_code = models.CharField(max_length=128, blank=True, default="", verbose_name="Артикул")
    expiration_date = models.DateField(blank=True, null=True, verbose_name="Срок годности")
    #image
    #category Foreign Key
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0, verbose_name="Цена продажи") #Цена продажи
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0, verbose_name="Себестоимость") #Себестоимость
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0, verbose_name="Цена закупки") #Цена закупки
    discount = models.IntegerField(blank=True, default=0, verbose_name="Скидка")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0, verbose_name="Кол-во")
    description = models.TextField(blank=True, max_length=1000, default="", verbose_name="Описание")

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='last_modified_by')
    last_modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "ID:{} - Name:{}".format(self.pk, self.name)

    # def get_absolute_url(self):
    #     return reverse('tables:product-detail', kwargs={'pk': self.pk})







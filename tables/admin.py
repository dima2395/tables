from django.contrib import admin
from .models import Product, Warehouse, Company
from accounts.models import Profile

# Register your models here.
admin.site.register(Product)
admin.site.register(Warehouse)
admin.site.register(Profile)
admin.site.register(Company)

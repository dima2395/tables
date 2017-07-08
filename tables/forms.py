from django import forms
from .models import Product, Company, Warehouse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'barcode', 'vendor_code', 'selling_price',
                  'cost_price', 'purchase_price', 'discount', 'quantity', 'description']




class EmployeeForm(UserCreationForm):
    # add_product = forms.BooleanField()
    # change_product = forms.BooleanField()
    # delete_product = forms.BooleanField()

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email', 'password1', 'password2']


class EmployeeEditForm(forms.ModelForm):
    # add_product = forms.BooleanField()
    # change_product = forms.BooleanField()
    # delete_product = forms.BooleanField()

    class Meta:
        model = User
        fields = ['first_name','last_name', 'email']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'legal_address', 'actual_address', 'telephone_number','email','website','description']


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address']
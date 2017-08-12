from django import forms
from .models import Product, Company, Warehouse, Client, Order, OrderProductsList, Service, OrderServicesList
from accounts.models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from djangoformsetjs.utils import formset_media_js



class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'vendor_code', 'barcode', 'unit','description']



class ServiceForm(forms.ModelForm):
    
    class Meta:
        model = Service
        fields = ['name', 'description']





class EmployeeForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args,**kwargs)
        self.fields['email'].required=True
        self.fields['first_name'].required=True
        self.fields['last_name'].required=True

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError("Это e-mail адрес уже используется. Пожалуйста используйте другой.")
        return email

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class EmployeeEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmployeeEditForm, self).__init__(*args,**kwargs)
        self.fields['email'].required=True
        self.fields['first_name'].required=True
        self.fields['last_name'].required=True

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError("Это e-mail адрес уже используется. Пожалуйста используйте другой.")
        return email

    class Meta:
        model = User
        fields = ['first_name','last_name', 'email']


class EmployeeChangePasswordForm(forms.Form):
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args,**kwargs)
        self.fields['telephone_number'].required=True


    class Meta:
        model = Profile
        fields = ['position', 'telephone_number']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'legal_address', 'actual_address', 'telephone_number', 'email', 'website', 'description']


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address']

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'telephone_number', 'description']


class OrderForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.none(), label='Клиент')

    class Meta:
        model = Order
        fields = ['client', 'urgency', 'comment', 'status', 'warehouse_confirmed', 'bookkeeping_confirmed']

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('client_qs')
        super(OrderForm, self).__init__(*args,**kwargs)
        self.fields['client'].queryset = qs

class OrderProductsListForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), label='Товар', required=True)

    class Meta:
        fields = ['product', 'quantity']
        model = OrderProductsList


    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('product_qs')
        super(OrderProductsListForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = qs


class OrderServicesListForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.none(), label='Услуга', required=True)

    class Meta:
        fields = ['service']

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('service_qs')
        super(OrderServicesListForm, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = qs





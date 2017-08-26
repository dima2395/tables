from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args,**kwargs)
        self.fields['username'].label='Логин'
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
        fields = ['username','email','first_name', 'last_name' ,'password1', 'password2']


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].required=True
        self.fields['last_name'].required=True


    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError("Это e-mail адрес уже используется. Пожалуйста используйте другой.")
        return email

    class Meta:
        model = User
        fields = ['first_name', 'last_name']



class ProfileAdditionalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telephone_number']


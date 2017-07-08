from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError("Это e-mail адрес уже используется. Пожалуйста используйте другой.")
        return email

    class Meta:
        model = User
        fields = ['username','email','password1', 'password2']



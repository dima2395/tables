from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from .forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login, logout

# Create your views here.
def signup(request):

    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                user.profile.is_owner = True
                user.profile.position = 'Manager'
                user.save()
                current_site = get_current_site(request)
                subject = 'Активируйте Ваш аккаунт'
                message = render_to_string('registration/activation_email.txt', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                #Здесь бы удалять пользователя если что-то пошло не так
                #Если емейл не дойдёт или он введён неверно, пользователь создастся, но подтвердить уже будет нельзя
                #Это ошибка которую надо будет решить в будующем
                user.email_user(subject, message)
                messages.success(request, 'Письмо активации было успешно отправлено на вашу почту')
            except:
                messages.error(request, 'Что-то пошло не так, попробуйте ещё раз')
                user.delete()
            return redirect(reverse('accounts:signup'))
    return render(request,'registration/registration.html', {'form': form})


def activate(request, uid64, token):
    logout(request)

    if uid64 and token:
        uid = urlsafe_base64_decode(uid64)
        try:
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse('tables:company-create'))





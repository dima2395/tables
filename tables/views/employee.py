from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site


from ..models import Company
from ..forms import EmployeeForm, EmployeeEditForm, ProfileForm, EmployeeChangePasswordForm





@login_required
def employees(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        return render(request, 'tables/employee/employees.html',{'company': company})
    else:
        return redirect(reverse('tables:index'))



@login_required
def employee_create(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    form = EmployeeForm(request.POST or None)
    profileForm = ProfileForm(request.POST or None)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            if form.is_valid() and profileForm.is_valid():
                try:
                    employee = form.save(commit=False)
                    profile = profileForm.save(commit=False)
                    employee.is_active = True
                    employee.save()
                    profile.user = employee
                    profile.save()
                    company.employees.add(employee)
                    #email send (we send password on email, this is insecure)
                    current_site = get_current_site(request)
                    subject = 'Вас добавили в компанию "{}"'.format(company.name)
                    message = render_to_string('registration/employee_registration.txt', {
                        'employee': employee,
                        'domain': current_site,
                        'company': company,
                        'manager': user,
                    })
                    #Здесь бы удалять пользователя если что-то пошло не так
                    #Если емейл не дойдёт или он введён неверно, пользователь создастся, но подтвердить уже будет нельзя
                    #Это ошибка которую надо будет решить в будующем
                    employee.email_user(subject, message)
                    messages.success(request, 'Сотрудник успешно добавлен, ему отправлено письмо с его логином и паролем')
                except Exception as e:
                    employee.delete()
                    messages.error(request, 'Что-то пошло не так, попробуйте ещё раз' )
                return redirect(reverse('tables:employee-create',kwargs={'company_pk': company.pk}))
        context = {
            'company': company,
            'form': form,
            'profileForm': profileForm,
        }
        return render(request, 'tables/employee/employee_create.html', context)
    else:
        return redirect(reverse('tables:index'))



@login_required
def employee_edit(request, company_pk, employee_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    employee = get_object_or_404(company.employees, pk=employee_pk)
    form = EmployeeEditForm(request.POST or None, instance=employee)
    profileForm = ProfileForm(request.POST or None, instance=employee.profile)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            if form.is_valid() and profileForm.is_valid():
                form.save()
                messages.success(request, 'Изменения сохранены')
                return redirect(reverse('tables:employee-edit',kwargs={'company_pk': company.pk, 'employee_pk':employee.pk}))
        context = {
            'company': company,
            'form': form,
            'profileForm': profileForm,
            'employee': employee,
        }
        return render(request, 'tables/employee/employee_edit.html', context)
    else:
        return redirect(reverse('tables:index'))



@login_required
def employee_delete(request, company_pk, employee_pk):
    
    company = get_object_or_404(Company, pk=company_pk)
    employee = get_object_or_404(company.employees, pk=employee_pk)
    data = dict()
    user = request.user

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            employee.delete()
            data['form_is_valid'] = True
        else:
            context = {
                'employee': employee,
                'company': company
            }
            data['html_form'] = render_to_string('tables/employee/employee_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))



@login_required
def employees_delete(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    data = dict()

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            
            ids = request.POST.get('ids').split(',')
            cleaned_ids = []
            for _id in ids:
                try:
                    number = int(_id)
                    cleaned_ids.append(number)
                except:
                    return HttpResponseForbidden()
            #vrode bi vse zbs
            company.employees.filter(pk__in=cleaned_ids).delete()
            data['form_is_valid'] = True

        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))

@login_required
def change_password(request, company_pk, employee_pk):
    company = get_object_or_404(Company, pk=company_pk)
    employee = get_object_or_404(User, pk=employee_pk)
    user = request.user
    form = EmployeeChangePasswordForm(request.POST or None)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if form.is_valid():
            employee.set_password(form.cleaned_data['password1'])
            employee.save()
            messages.success(request, 'Пароль пользователя "{}" успешно изменён.'.format(employee.username))
            return redirect(reverse('tables:employee-change-password', kwargs={'company_pk': company.pk, 'employee_pk':employee.pk}))
        return render(request, 'tables/employee/employee_change_password.html', {'company': company, 'employee': employee, 'form': form})
    else:
        return redirect(reverse('tables:index'))


@login_required
def employees_list(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user.profile.in_company(company.pk) and user.profile.is_manager():

        employees = company.employees.all()

        result = []
        for employee in employees:
            result.append({
                'pk': employee.pk,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'username': employee.username,
                'position': employee.profile.get_position_display(),
                'telephone_number': employee.profile.telephone_number,
                'email': employee.email,
                'actions': {
                    'edit': reverse('tables:employee-edit', kwargs={'company_pk': company.pk, 'employee_pk':employee.pk}),
                    'change_password': reverse('tables:employee-change-password', kwargs={'company_pk': company.pk, 'employee_pk':employee.pk}),
                    'delete': reverse('tables:employee-delete', kwargs={'company_pk': company.pk, 'employee_pk':employee.pk}),
                }
            })

        return result
    else:
        return redirect(reverse('tables:index'))

@login_required
def employees_json(request, company_pk):
    return JsonResponse({'data': employees_list(request, company_pk)}, safe=False)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Company
from ..forms import EmployeeForm, EmployeeEditForm




@login_required
def employees(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user == company.owner:
        employees = company.employees.all()
        return render(request, 'tables/company/employee/employees.html',{'employees': employees, 'company': company})
    else:
        return redirect(reverse('tables:index'))

@login_required
def save_employee_form(request, company_pk, form, template_name):
    data = dict()
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if request.method == 'POST':
        if form.is_valid():
            employee = form.save(commit=False)
            employee.is_active = True
            employee.save()
            company.employees.add(employee)

            data['form_is_valid'] = True
            employees = company.employees.all()
            data['employees_list_count'] = employees.count()
            data['employees_list'] = render_to_string('tables/company/employee/employees_list.html', {'employees': employees, 'company': company})
        else:
            data['form_is_valid'] = False
    context = {'form': form, 'company': company}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def employee_create(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user == company.owner:
        if request.method == 'POST':
            form = EmployeeForm(request.POST)
        else:
            form = EmployeeForm()
        return save_employee_form(request, company_pk, form, 'tables/company/employee/employee_create_form.html')
    else:
        return redirect(reverse('tables:index'))


@login_required
def employee_edit(request, company_pk, employee_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    employee = get_object_or_404(User, pk=employee_pk)

    if user == company.owner and employee in company.employees.all():
        if request.method == 'POST':
            form = EmployeeEditForm(request.POST, instance=employee)
        else:
            form = EmployeeEditForm(instance=employee)
        return save_employee_form(request, company_pk, form, 'tables/company/employee/employee_edit_form.html')
    else:
        return redirect(reverse('tables:index'))


@login_required
def employee_delete(request, company_pk, employee_pk):
    employee = get_object_or_404(User, pk=employee_pk)
    company = get_object_or_404(Company, pk=company_pk)
    data = dict()
    user = request.user

    if user == company.owner and employee in company.employees.all():
        if request.method == 'POST':
            employee.delete()
            data['form_is_valid'] = True
            employees = company.employees.all()
            data['employees_list_count'] = employees.count()
            data['employees_list'] = render_to_string('tables/company/employee/employees_list.html', {'employees': employees, 'company': company})
        else:
            context = {'employee': employee, 'company': company}
            data['html_form'] = render_to_string('tables/company/employee/employee_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))
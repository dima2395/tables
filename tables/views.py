from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .models import Product, Warehouse, Company
from .forms import ProductForm, EmployeeForm, EmployeeEditForm, CompanyForm, WarehouseForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core import serializers
import json
from collections import OrderedDict
from django.urls import reverse
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'tables/index.html')


#is used for setting active menu item
@login_required
def company(request, pk):
    return HttpResponse('LOL')

@login_required
def company_create(request):
    form = CompanyForm(request.POST or None)
    user = request.user
    if user.profile.is_owner:
        if request.method == 'POST':
            if form.is_valid():
                company = form.save(commit=False)
                company.owner = user
                company.save()
                # messages.success(request, 'Компания успешно создана.')
                return redirect(reverse('tables:warehouses', kwargs={'company_pk': company.pk}))
                #return redirect to company page
        return render(request, 'tables/company/company_create.html', {'form': form})


@login_required
def company_edit(request, pk):
    user = request.user
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if company.owner == user:
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Изменения сохранены успешно.')
                return redirect(reverse('tables:company-edit', kwargs={'pk': company.pk}))
            except:
                messages.error(request, 'Что-то пошло не так, попробуйте ещё раз.')


        return render(request, 'tables/company/company_edit.html', {'form': form, 'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def company_delete(request, pk):
    user = request.user
    company = get_object_or_404(Company, pk=pk)
    if company.owner == user:
        if request.method == 'POST':
            company.delete()
            return redirect(reverse('tables:index')) 
    else:
        return redirect(reverse('tables:index'))



@login_required
def warehouses(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouses = Warehouse.objects.filter(company=company)

    if (user == company.owner or user in company.employees.all()):
        return render(request, 'tables/company/warehouse/warehouses.html', {'company': company, 'warehouses': warehouses})
    else:
        return redirect(reverse('tables:index'))


@login_required
def save_warehouse_form(request, company_pk, form, template_name):
    data = dict()
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if request.method == 'POST':
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.company = company
            warehouse.save()

            data['form_is_valid'] = True
            warehouses = Warehouse.objects.filter(company=company)
            data['warehouses_list_count'] = warehouses.count()
            data['warehouses_list'] = render_to_string('tables/company/warehouse/warehouses_list.html', {'warehouses': warehouses})

        else:
            data['form_is_valid'] = False
    context = {'form': form, 'company': company}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)



@login_required
def warehouse_create(request, company_pk):
    user = request.user
    company = get_object_or_404(Company,pk=company_pk)

    if user == company.owner:

        if request.method == 'POST':
            form = WarehouseForm(request.POST)
        else:
            form = WarehouseForm()
        return save_warehouse_form(request, company_pk, form, 'tables/company/warehouse/warehouse_create_form.html')
    else:
        return redirect(reverse('tables:index'))


@login_required
def warehouse_edit(request, company_pk, warehouse_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)

    if warehouse.company == company and user == warehouse.company.owner:

        if request.method == 'POST':
            form = WarehouseForm(request.POST, instance=warehouse)
        else:
            form = WarehouseForm(instance=warehouse)
        return save_warehouse_form(request, company_pk, form, 'tables/company/warehouse/warehouse_edit_form.html')
    else:
        return redirect(reverse('tables:index'))

@login_required
def warehouse_delete(request, company_pk, warehouse_pk):
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    company = get_object_or_404(Company, pk=company_pk)
    data = dict()
    user = request.user
    if warehouse.company == company and user == warehouse.company.owner:
        if request.method == 'POST':
            warehouse.delete()
            data['form_is_valid'] = True
            warehouses = Warehouse.objects.filter(company=company)
            data['warehouses_list_count'] = warehouses.count()
            data['warehouses_list'] = render_to_string('tables/company/warehouse/warehouses_list.html', {'warehouses': warehouses})
        else:
            context = {'warehouse': warehouse}
            data['html_form'] = render_to_string('tables/company/warehouse/warehouse_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))



@login_required
#view for first datatable initialization wraps products_list
def products_json(request, company_pk, warehouse_pk):
    return JsonResponse({'data': products_list(request, company_pk, warehouse_pk) }, safe=False)


@login_required
def products_list(request, company_pk, warehouse_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)

    if user == warehouse.company.owner and warehouse.company == company:
        products = Product.objects.filter(warehouse=warehouse).order_by('-created_at')

        result = []

        buttons ="<button type=\"button\" class=\"btn btn-warning btn-sm js-edit-product\" data-url=\"{edit_url}\"><span class=\"fa fa-pencil\"></span></button><button type=\"button\" class=\"btn btn-danger btn-sm js-delete-product\" data-url=\"{delete_url}\"><span class=\"fa fa-trash-o\"></span></button>"
        for product in products:
            result.append(OrderedDict([
                ('pk', product.pk),
                ('name', product.name),
                ('barcode', product.barcode),
                ('vendor_code', product.vendor_code),
                ('selling_price', str(product.selling_price)),
                ('cost_price', str(product.cost_price)),
                ('purchase_price', str(product.purchase_price)),
                ('discount', str(product.discount)),
                ('quantity', str(product.quantity)),
                ('description', product.description),
                ('actions', buttons.format(edit_url=reverse('tables:product-edit', kwargs={'company_pk': company.pk, 'warehouse_pk': warehouse.pk, 'product_pk': product.pk }),
                                            delete_url=reverse('tables:product-delete', kwargs={'company_pk': company.pk, 'warehouse_pk':warehouse.pk, 'product_pk': product.pk }))),
            ]))
        return result
    else:
        return redirect(reverse('tables:index'))

@login_required
def products(request, company_pk, warehouse_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)

    if user == warehouse.company.owner and warehouse.company == company:
        return render(request, 'tables/product/products.html', {'company': company, 'warehouse': warehouse})
    else:
        return redirect(reverse('tables:index'))

@login_required
def save_product_form(request, company_pk, warehouse_pk, form, template_name):
    data = dict()
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            #if doesnotexist this is create action else it is update action
            try:
                product.created_by
            except User.DoesNotExist:
                product.created_by = user
            try:
                product.warehouse
            except Warehouse.DoesNotExist:
                product.warehouse = warehouse


            product.last_modified_by = user

            # product.warehouse = warehouse
            product.save()
            data['form_is_valid'] = True
            data['products_list'] = products_list(request, company_pk, warehouse_pk)
        else:
            data['form_is_valid'] = False
    context = {'form': form, 'company': company, 'warehouse': warehouse}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)



@login_required
def product_create(request, company_pk, warehouse_pk):
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    user = request.user

    if user == warehouse.company.owner and warehouse.company == company:
        if request.method == 'POST':
            form = ProductForm(request.POST)
        else:
            form = ProductForm()
        return save_product_form(request, company_pk, warehouse_pk, form, 'tables/product/product_create_form.html')
    else:
        return redirect(reverse('tables:index'))


@login_required
def product_edit(request, company_pk, warehouse_pk, product_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    product = get_object_or_404(Product, pk=product_pk)

    if user == warehouse.company.owner and warehouse.company == company and product.warehouse == warehouse:
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
        else:
            form = ProductForm(instance=product)
        return save_product_form(request, company_pk, warehouse_pk, form, 'tables/product/product_edit_form.html')
    else:
        return redirect(reverse('tables:index'))

@login_required
def product_delete(request, company_pk, warehouse_pk, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    data = dict()
    user = request.user

    if user == warehouse.company.owner and warehouse.company == company and product.warehouse == warehouse:
        if request.method == 'POST':
            product.delete()
            data['form_is_valid'] = True
            data['products_list'] = products_list(request, company_pk, warehouse_pk)
        else:
            context = {'product': product, 'company': company, 'warehouse': warehouse}
            data['html_form'] = render_to_string('tables/product/product_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))


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


# @login_required
# def employee_create(request, company_pk):
#     user = request.user
#     company = get_object_or_404(Company, pk=company_pk)
#     form = EmployeeForm(request.POST or None)
#     if user.profile.is_owner:
#         if form.is_valid():
#             try:
#                 employee = form.save(commit=False)
#                 employee.is_active = True
#                 employee.save()
#                 company.employees.add(employee)
#                 messages.success(request, 'Сотрудник успешно добавлен.')
#             except:
#                 employee.delete()
#                 messages.success(request, 'Что-то пошло не так, попробуйте ещё раз.')
#             return redirect(reverse('tables:employee-create', kwargs={'company_pk': company_pk}))
#         return render(request, 'tables/company/employee/employees.html', {'form': form, 'employees': company.employees.all()})


# @login_required
# def employees(request):
#     form = EmployeeForm()
#     user = request.user
#     if user.profile.is_owner:
#         employees = User.objects.filter(profile__owner=user).exclude(pk=user.pk)
#         if request.method == 'POST':
#             form = EmployeeForm(request.POST)
#             if form.is_valid():
#                 employee = form.save(commit=False)
#                 employee.is_active = True
#                 employee.save()
                
#                 #if something goes wrong
#                 try:
#                     employee.profile.owner = user

#                     #handle permissions
#                     permissions_add = []
#                     permissions_remove = []
#                     content_type = ContentType.objects.get_for_model(Product)
#                     if form.cleaned_data['add_product']:
#                         permissions_add.append(Permission.objects.get(codename='add_product', content_type=content_type))
#                     else:
#                         permissions_remove.append(Permission.objects.get(codename='add_product', content_type=content_type))

#                     if form.cleaned_data['delete_product']:
#                         permissions_add.append(Permission.objects.get(codename='delete_product', content_type=content_type))
#                     else:
#                         permissions_remove.append(Permission.objects.get(codename='delete_product', content_type=content_type))

#                     if form.cleaned_data['change_product']:
#                         permissions_add.append(Permission.objects.get(codename='change_product', content_type=content_type))
#                     else:
#                         permissions_remove.append(Permission.objects.get(codename='change_product', content_type=content_type))

#                     if permissions_add:
#                         employee.user_permissions.add(*permissions_add)
#                     if permissions_remove:
#                         employee.user_permissions.remove(*permissions_remove)
#                 except:
#                     employee.delete()
#                     messages.error(request, 'Что-то пошло не так, попробуйте ещё раз.')
#                 else:
#                     employee.save()
#                     messages.success(request, 'Сотрудник успешно добавлен')

#                 return redirect('tables:employees')
#         return render(request, 'tables/employees.html', {'employees': employees, 'form': form})
#     else:
#         return redirect('tables:products')



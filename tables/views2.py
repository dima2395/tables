from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .models import Product, Warehouse, Company, Client, OrderProductsList, Order, Service, OrderServicesList
from .forms import ProductForm, EmployeeForm, EmployeeEditForm, CompanyForm, WarehouseForm, \
                   ClientForm, OrderForm, OrderProductsListForm, ServiceForm, OrderServicesListForm
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
from django.http import HttpResponse, HttpResponseForbidden
from django.forms import modelformset_factory
from datetime import datetime
from django.db.utils import IntegrityError

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
    form = WarehouseForm(request.POST or None)

    if user == company.owner:
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

        
        for product in products:
            result.append(OrderedDict([
                ('pk', product.pk),
                ('name', product.name),
                ('barcode', product.barcode),
                ('vendor_code', product.vendor_code),
                ('unit', product.unit),
                # ('selling_price', str(product.selling_price)),
                # ('cost_price', str(product.cost_price)),
                # ('purchase_price', str(product.purchase_price)),
                # ('discount', str(product.discount)),
                # ('quantity', str(product.quantity)),
                ('description', product.description),
                ('actions', {
                            'delete': reverse('tables:product-delete', kwargs={'company_pk': company.pk, 'warehouse_pk':warehouse.pk, 'product_pk': product.pk }),
                            'edit': reverse('tables:product-edit', kwargs={'company_pk': company.pk, 'warehouse_pk':warehouse.pk, 'product_pk': product.pk })
                            }
                )
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
def product_create(request, company_pk, warehouse_pk):
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    user = request.user
    form = ProductForm(request.POST or None)

    if user == warehouse.company.owner and warehouse.company == company:
        if request.method == 'POST':
            if form.is_valid():
                product = form.save(commit=False)
                product.warehouse = warehouse
                product.created_by = user
                product.last_modified_by = user
                product.save()
                messages.success(request, 'Товар успешно добавлен')
                return redirect(reverse('tables:product-create',kwargs={'company_pk': company_pk, 'warehouse_pk': warehouse_pk}))
        return render(request, 'tables/product/product_create.html', {'company': company, 'warehouse':warehouse, 'form': form})
    else:
        return redirect(reverse('tables:index'))


@login_required
def product_edit(request, company_pk, warehouse_pk, product_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    product = get_object_or_404(Product, pk=product_pk)
    form = ProductForm(request.POST or None, instance=product)

    if user == warehouse.company.owner and warehouse.company == company and product.warehouse == warehouse:
        if request.method == 'POST':
            if form.is_valid():
                updated_product = form.save(commit=False)
                updated_product.last_modified_by = user
                updated_product.last_modified_at = datetime.now()
                try:
                    updated_product.save()
                    messages.success(request, 'Обновления сохранены')
                except:
                    messages.error(request, 'Что-то пошло не так')
                return redirect(reverse('tables:product-edit',kwargs={'company_pk': company_pk, 'warehouse_pk': warehouse_pk, 'product_pk': product.pk}))


        return render(request, 'tables/product/product_edit.html', {'company': company, 'warehouse':warehouse, 'product': product, 'form': form})
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


#Deletes list of products
@login_required
def products_delete(request, company_pk, warehouse_pk):
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        print('\n\n\n',request.POST, '\n\n\n')
        ids = request.POST.get('ids').split(',')
        cleaned_ids = []
        for _id in ids:
            try:
                number = int(_id)
                cleaned_ids.append(number)
            except:
                return HttpResponseForbidden()
        #vrode bi vse zbs
        Product.objects.filter(pk__in=cleaned_ids, warehouse=warehouse, warehouse__company=company).delete()
        data['form_is_valid'] = True
        data['products_list'] = products_list(request, company_pk, warehouse_pk)

    return JsonResponse(data)


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
@login_required
def client_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    form = ClientForm(request.POST or None);
    user = request.user
    clients = Client.objects.filter(company=company)
    if request.method == 'POST':
        if form.is_valid():
            client = form.save(commit=False)
            client.company = company
            client.save()
            messages.success(request, 'Клиент успешно добавлен')
            return redirect(reverse('tables:client-create', kwargs={'company_pk': company.pk}))
    
    return render(request, 'tables/client/client_create.html', {'company': company, 'form': form, 'clients': clients})


@login_required
def clients(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    return render(request, 'tables/client/clients.html', {'company': company})


@login_required
def clients_list(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    clients = Client.objects.filter(company=company)
    result = []

    for client in clients:
        result.append({
            'pk': client.pk,
            'name': client.name,
            'description': client.description,
            'address': client.address,
            'telephone_number': client.telephone_number,
            'actions': {
                'edit': reverse('tables:client-edit', kwargs={'company_pk': company.pk, 'client_pk':client.pk}),
                'delete': reverse('tables:client-delete', kwargs={'company_pk': company.pk, 'client_pk':client.pk})
            }
        })
    return result



@login_required
def clients_json(request, company_pk):
    return JsonResponse({'data': clients_list(request, company_pk)}, safe=False)



@login_required
def client_edit(request, company_pk, client_pk):
    company = get_object_or_404(Company, pk=company_pk)
    client = get_object_or_404(Client, pk=client_pk)
    form = ClientForm(request.POST or None, instance=client);
    user = request.user
    clients = Client.objects.filter(company=company)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены')
            return redirect(reverse('tables:client-edit', kwargs={'company_pk': company.pk, 'client_pk':client.pk }))
    context = {
        'company': company,
        'client': client,
        'form': form
    }
    return render(request, 'tables/client/client_edit.html', context)


@login_required
def client_delete(request, company_pk, client_pk):
    company = get_object_or_404(Company, pk=company_pk)
    client = get_object_or_404(Client, pk=client_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        client.delete()
        data['form_is_valid'] = True
        data['clients_list'] = clients_list(request, company_pk)
    else:
        context = {
            'client': client,
            'company': company,
        }
        data['html_form'] = render_to_string('tables/client/client_delete_form.html', context, request=request)
    return JsonResponse(data)



@login_required
def clients_delete(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        ids = request.POST.get('ids').split(',')
        cleaned_ids = []
        for _id in ids:
            try:
                number = int(_id)
                cleaned_ids.append(number)
            except:
                return HttpResponseForbidden()
        Client.objects.filter(pk__in=cleaned_ids, company=company).delete()
        data['form_is_valid'] = True
        data['clients_list'] = clients_list(request, company_pk)
    return JsonResponse(data)


@login_required
def order_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    orderForm = OrderForm(request.POST or None, client_qs=Client.objects.filter(company=company));
    user = request.user

    product_qs = Product.objects.filter(warehouse__company=company)
    OrderProductsListFormSet = modelformset_factory(OrderProductsList,
                                                    form=OrderProductsListForm,
                                                    extra=0,
                                                    can_delete=True)
    productsFormset = OrderProductsListFormSet(request.POST or None,
                                               form_kwargs={'product_qs': product_qs},
                                               queryset=OrderProductsList.objects.none(),
                                               prefix='products')

    service_qs = Service.objects.filter(company=company)
    OrderServicesListFormSet = modelformset_factory(OrderServicesList,
                                                    form=OrderServicesListForm,
                                                    extra=0,
                                                    can_delete=True)
    servicesFormset = OrderServicesListFormSet(request.POST or None,
                                               form_kwargs={'service_qs': service_qs},
                                               queryset=OrderServicesList.objects.none(),
                                               prefix='services')

    if request.method == 'POST':
        if productsFormset.is_valid() and servicesFormset.is_valid() and orderForm.is_valid():
            order = orderForm.save(commit=False)
            order.company = company
            order.created_by = user
            order.save()
            for form in productsFormset:
                if form not in productsFormset.deleted_forms:
                    #Если не выбрать никакой пункт вылетает ошибка
                    orderProduct = form.save(commit=False)
                    orderProduct.order = order
                    try:
                        orderProduct.save()
                    except IntegrityError:
                        pass
            for form in servicesFormset:
                if form not in servicesFormset.deleted_forms:
                    #Если не выбрать никакой пункт вылетает ошибка
                    orderService = form.save(commit=False)
                    orderService.order = order
                    try:
                        orderService.save()
                    except IntegrityError:
                        pass
            messages.success(request, 'Заказ добавлен')
            return redirect(reverse('tables:order-create', kwargs={'company_pk': company.pk}))

    context = {
        'company': company,
        'orderForm': orderForm,
        'productsFormset': productsFormset,
        'servicesFormset': servicesFormset,
        'orders': Order.objects.filter(company=company).order_by('-created_at')
    }
    return render(request, 'tables/order/order_create.html', context)


@login_required
def orders_list(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    orders = Order.objects.filter(company=company).order_by('-created_at')
    result = []

    for order in orders:
        
        products = []
        for orderProduct in order.orderproductslist_set.all():
            products.append({
                'name': orderProduct.product.name,
                'quantity': orderProduct.quantity,
                'unit': orderProduct.product.unit,
            })

        services = []
        for orderService in order.orderserviceslist_set.all():
            services.append({
                'name': orderService.service.name,
            })

        result.append({
            'pk': order.pk,
            'client': order.client.name,
            'urgency': {
                'label': order.get_urgency_display(),
                'value': order.urgency
            },
            'created_at': order.created_at.strftime('%d %B %Y, %H:%M'),
            'created_by': order.created_by.get_full_name(),
            'comment': order.comment,
            'products': products,
            'services': services,
        })

    return result

@login_required
def orders_json(request, company_pk):
    print('\n\n\nLUL:\n', {'data':orders_list(request, company_pk)})
    return JsonResponse({'data':orders_list(request, company_pk)}, safe=False)


@login_required
def orders(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user

    return render(request, 'tables/order/orders.html', {'company': company})


@login_required
def services(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    return render(request, 'tables/service/services.html', {'company': company})


@login_required
def services_list(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    services = Service.objects.filter(company=company)
    result = []

    for service in services:
        result.append({
            'pk': service.pk,
            'name': service.name,
            'description': service.description,
            'actions': {
                'delete': reverse('tables:service-delete', kwargs={'company_pk': company.pk, 'service_pk':service.pk}),
                'edit': reverse('tables:service-edit', kwargs={'company_pk': company.pk, 'service_pk':service.pk})
            }
        })
    return result


@login_required
def services_json(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    return JsonResponse({'data': services_list(request, company_pk)}, safe=False)

@login_required
def service_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    form = ServiceForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            service = form.save(commit=False)
            service.company = company
            service.save()
            messages.success(request, 'Услуга добавлена')
            return redirect(reverse('tables:service-create', kwargs={'company_pk': company.pk}))
    context = {
        'company': company,
        'form': form,
        'services': Service.objects.filter(company=company)
    }

    return render(request, 'tables/service/service_create.html', context)

@login_required
def service_edit(request, company_pk, service_pk):
    company = get_object_or_404(Company, pk=company_pk)
    service = Service.objects.get(pk=service_pk)
    user = request.user
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены')
            return redirect(reverse('tables:service-edit', kwargs={'company_pk': company.pk, 'service_pk':service.pk }))
    context = {
        'company': company,
        'service': service,
        'form': form
    }
    return render(request, 'tables/service/service_edit.html', context)


@login_required
def service_delete(request, company_pk, service_pk):
    company = get_object_or_404(Company, pk=company_pk)
    service = Service.objects.get(pk=service_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        service.delete()
        data['form_is_valid'] = True
        data['services_list'] = services_list(request, company_pk)
    else:
        context = {
            'service': service,
            'company': company
        }
        data['html_form'] = render_to_string('tables/service/service_delete_form.html', context, request=request)
    return JsonResponse(data)

@login_required
def services_delete(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        print('\n\n\n',request.POST, '\n\n\n')
        ids = request.POST.get('ids').split(',')
        cleaned_ids = []
        for _id in ids:
            try:
                number = int(_id)
                cleaned_ids.append(number)
            except:
                return HttpResponseForbidden()
        Service.objects.filter(pk__in=cleaned_ids, company=company).delete()
        data['form_is_valid'] = True
        data['services_list'] = services_list(request, company_pk)
    return JsonResponse(data)

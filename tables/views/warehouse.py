from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..models import Company, Warehouse
from ..forms import WarehouseForm







@login_required
def warehouses(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouses = Warehouse.objects.filter(company=company)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        return render(request, 'tables/warehouse/warehouses.html', {'company': company, 'warehouses': warehouses})
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
            data['warehouses_list'] = render_to_string('tables/warehouse/warehouses_list.html', {'warehouses': warehouses})

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

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        return save_warehouse_form(request, company_pk, form, 'tables/warehouse/warehouse_create_form.html')
    else:
        return redirect(reverse('tables:index'))


@login_required
def warehouse_edit(request, company_pk, warehouse_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, company=company, pk=warehouse_pk)

    if user.profile.in_company(company.pk) and user.profile.is_manager():

        if request.method == 'POST':
            form = WarehouseForm(request.POST, instance=warehouse)
        else:
            form = WarehouseForm(instance=warehouse)
        return save_warehouse_form(request, company_pk, form, 'tables/warehouse/warehouse_edit_form.html')
    else:
        return redirect(reverse('tables:index'))

@login_required
def warehouse_delete(request, company_pk, warehouse_pk):
    company = get_object_or_404(Company, pk=company_pk)
    warehouse = get_object_or_404(Warehouse, company=company, pk=warehouse_pk)
    
    data = dict()
    user = request.user
    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            warehouse.delete()
            data['form_is_valid'] = True
            warehouses = Warehouse.objects.filter(company=company)
            data['warehouses_list_count'] = warehouses.count()
            data['warehouses_list'] = render_to_string('tables/warehouse/warehouses_list.html', {'warehouses': warehouses})
        else:
            context = {'warehouse': warehouse}
            data['html_form'] = render_to_string('tables/warehouse/warehouse_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..models import Company, Warehouse, Product
from ..forms import ProductForm



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
            result.append({
                'pk': product.pk,
                'name': product.name,
                'barcode': product.barcode,
                'vendor_code': product.vendor_code,
                'unit': product.unit,
                # 'selling_price': str(product.selling_price),
                # 'cost_price': str(product.cost_price),
                # 'purchase_price': str(product.purchase_price),
                # 'discount': str(product.discount),
                # 'quantity': str(product.quantity),
                'description': product.description,
                'actions': {
                    'delete': reverse('tables:product-delete', kwargs={'company_pk': company.pk, 'warehouse_pk':warehouse.pk, 'product_pk': product.pk }),
                    'edit': reverse('tables:product-edit', kwargs={'company_pk': company.pk, 'warehouse_pk':warehouse.pk, 'product_pk': product.pk })
                }
                
            })
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
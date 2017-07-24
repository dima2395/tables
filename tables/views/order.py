from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils import timezone

from ..models import Company, Service, Client, Order, Product, OrderProductsList, OrderServicesList
from ..forms import OrderProductsListForm, OrderServicesListForm, OrderForm




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
def order_edit(request, company_pk, order_pk):
    company = get_object_or_404(Company, pk=company_pk)
    order = get_object_or_404(Order, pk=order_pk)
    orderForm = OrderForm(request.POST or None, instance=order, client_qs=Client.objects.filter(company=company));

    product_qs = Product.objects.filter(warehouse__company=company)
    OrderProductsListFormSet = modelformset_factory(OrderProductsList,
                                                    form=OrderProductsListForm,
                                                    extra=0,
                                                    can_delete=True)
    productsFormset = OrderProductsListFormSet(request.POST or None,
                                               form_kwargs={'product_qs': product_qs},
                                               queryset=OrderProductsList.objects.filter(order=order),
                                               prefix='products')

    service_qs = Service.objects.filter(company=company)
    OrderServicesListFormSet = modelformset_factory(OrderServicesList,
                                                    form=OrderServicesListForm,
                                                    extra=0,
                                                    can_delete=True)
    servicesFormset = OrderServicesListFormSet(request.POST or None,
                                               form_kwargs={'service_qs': service_qs},
                                               queryset=OrderServicesList.objects.filter(order=order),
                                               prefix='services')

    if request.method == 'POST':
        if productsFormset.is_valid() and servicesFormset.is_valid() and orderForm.is_valid():

            for form in productsFormset:
                if form not in productsFormset.deleted_forms:
                    #Если не выбрать никакой пункт вылетает ошибка
                    orderProduct = form.save(commit=False)
                    orderProduct.order = order
                    try:
                        orderProduct.save()
                    except IntegrityError:
                        pass
                else:
                    if form.instance.pk is not None:
                        form.instance.delete()

            for form in servicesFormset:
                if form not in servicesFormset.deleted_forms:
                    #Если не выбрать никакой пункт вылетает ошибка
                    orderService = form.save(commit=False)
                    orderService.order = order
                    try:
                        orderService.save()
                    except IntegrityError:
                        pass
                else:
                    if form.instance.pk is not None:
                        form.instance.delete()

            order.save()
            messages.success(request, 'Изменения сохранены')
            return redirect(reverse('tables:order-edit', kwargs={'company_pk': company.pk, 'order_pk': order.pk}))

    context = {
        'company': company,
        'orderForm': orderForm,
        'productsFormset': productsFormset,
        'servicesFormset': servicesFormset,
        'order': order,
        'orders': Order.objects.filter(company=company).order_by('-created_at')
    }
    return render(request, 'tables/order/order_edit.html', context)



@login_required
def order_delete(request, company_pk, order_pk):
    company = get_object_or_404(Company, pk=company_pk)
    order = get_object_or_404(Order, pk=order_pk)
    user = request.user
    data = dict()

    if request.method == 'POST':
        order.delete()
        data['form_is_valid'] = True
        data['orders_list'] = orders_list(request, company_pk)
    else:
        context = {
            'order': order,
            'company': company,
        }
        data['html_form'] = render_to_string('tables/order/order_delete_form.html', context, request=request)
    return JsonResponse(data)



@login_required
def orders_delete(request, company_pk):
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
        Order.objects.filter(pk__in=cleaned_ids, company=company).delete()
        data['form_is_valid'] = True
        data['orders_list'] = orders_list(request, company_pk)
    return JsonResponse(data)



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
            'created_at': timezone.localtime(order.created_at).strftime('%d %B %Y, %H:%M'),
            'created_by': order.created_by.get_full_name(),
            'comment': order.comment,
            'products': products,
            'services': services,
            'actions': {
                'edit': reverse('tables:order-edit', kwargs={'company_pk': company.pk, 'order_pk':order.pk}),
                'delete': reverse('tables:order-delete', kwargs={'company_pk': company.pk, 'order_pk':order.pk}),
            }
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
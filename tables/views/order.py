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
from babel.dates import format_datetime
from django.utils.translation import get_language
from ..models import Company, Service, Client, Order, Product, OrderProductsList, OrderServicesList
from ..forms import OrderProductsListForm, OrderServicesListForm, OrderForm




@login_required
def order_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        orderForm = OrderForm(request.POST or None, client_qs=Client.objects.filter(company=company));

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
    else:
        return redirect(reverse('tables:index'))

@login_required
def order_edit(request, company_pk, order_pk):
    company = get_object_or_404(Company, pk=company_pk)
    order = get_object_or_404(Order, company=company, pk=order_pk)
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
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
    else:
        return redirect(reverse('tables:index'))



@login_required
def order_delete(request, company_pk, order_pk):
    company = get_object_or_404(Company, pk=company_pk)
    order = get_object_or_404(Order, company=company, pk=order_pk)
    user = request.user
    data = dict()

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):

        if request.method == 'POST':
            order.delete()
            data['form_is_valid'] = True
        else:
            context = {
                'order': order,
                'company': company,
            }
            data['html_form'] = render_to_string('tables/order/order_delete_form.html', context, request=request)
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))



@login_required
def orders_delete(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    data = dict()

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):

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
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))



@login_required
def orders_list(request, company_pk, filtered='all'):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    result = []

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):

        if filtered == 'all':
            orders = Order.objects.filter(company=company).order_by('-created_at')
        elif filtered == 'processing':
            orders = Order.objects.filter(company=company, status='processing').order_by('-created_at')
        elif filtered == 'completed':
            orders = Order.objects.filter(company=company, status='completed').order_by('-created_at')
        elif filtered == 'suspended':
            orders = Order.objects.filter(company=company, status='suspended').order_by('-created_at')

        #display only agent's orders
        if user.profile.is_agent():
            orders = orders.filter(created_by=user)


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
                'created_at': {
                    'date_str': format_datetime(timezone.localtime(order.created_at), 'd MMMM Y, HH:mm', locale=get_language()),
                    'date_value': timezone.localtime(order.created_at).strftime('%Y%m%d%H%M')


                },
                'comment': order.comment,
                'products': products,
                'services': services,
                'status': {
                    'label': order.get_status_display(),
                    'value': order.status,
                },
                'confirmations': {
                    'warehouse': order.warehouse_confirmed,
                    'bookkeeping': order.bookkeeping_confirmed
                },
                'actions': {
                    'edit': reverse('tables:order-edit', kwargs={'company_pk': company.pk, 'order_pk':order.pk}),
                    'delete': reverse('tables:order-delete', kwargs={'company_pk': company.pk, 'order_pk':order.pk}),
                },
                'agent': {
                    'full_name': order.created_by.get_full_name(),
                    'username': order.created_by.username
                }
            })

        return result
    else:
        return redirect(reverse('tables:index'))

@login_required
def orders_json(request, company_pk):
    
    return JsonResponse({'data':orders_list(request, company_pk)}, safe=False)


@login_required
def orders(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        return render(request, 'tables/order/orders.html', {'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def orders_processing(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user
    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        return render(request, 'tables/order/orders_processing.html', {'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def orders_processing_json(request, company_pk):
    return JsonResponse({'data':orders_list(request, company_pk, filtered='processing')}, safe=False)



@login_required
def orders_completed(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        return render(request, 'tables/order/orders_completed.html', {'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def orders_completed_json(request, company_pk):
    
    return JsonResponse({'data':orders_list(request, company_pk, filtered='completed')}, safe=False)


@login_required
def orders_suspended(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        return render(request, 'tables/order/orders_suspended.html', {'company': company})
    else:
        return redirect(reverse('tables:index'))

@login_required
def orders_suspended_json(request, company_pk):
    return JsonResponse({'data':orders_list(request, company_pk, filtered='suspended')}, safe=False)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..models import Company, Service
from ..forms import ServiceForm






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
    return JsonResponse(data)
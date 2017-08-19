from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..models import Company, Client
from ..forms import ClientForm





@login_required
def client_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    form = ClientForm(request.POST or None);
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        if request.method == 'POST':
            if form.is_valid():
                client = form.save(commit=False)
                client.company = company
                client.save()
                messages.success(request, 'Клиент успешно добавлен')
                return redirect(reverse('tables:client-create', kwargs={'company_pk': company.pk}))
        
        return render(request, 'tables/client/client_create.html', {'company': company, 'form': form})
    else:
        return redirect(reverse('tables:index'))


@login_required
def clients(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        return render(request, 'tables/client/clients.html', {'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def clients_list(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
        clients = Client.objects.filter(company=company)
        result = []

        for client in clients:
            current = {
                'pk': client.pk,
                'name': client.name,
                'description': client.description,
                'address': client.address,
                'telephone_number': client.telephone_number,
                'actions': {
                    'edit': reverse('tables:client-edit', kwargs={'company_pk': company.pk, 'client_pk':client.pk}),
                    
                }
            }
            if user.profile.is_manager():
                current['actions']['delete'] = reverse('tables:client-delete', kwargs={'company_pk': company.pk, 'client_pk':client.pk})
            result.append(current)
        return result
    else:
        return redirect(reverse('tables:index'))



@login_required
def clients_json(request, company_pk):
    return JsonResponse({'data': clients_list(request, company_pk)}, safe=False)



@login_required
def client_edit(request, company_pk, client_pk):
    company = get_object_or_404(Company, pk=company_pk)
    client = get_object_or_404(Client, company=company, pk=client_pk)
    form = ClientForm(request.POST or None, instance=client);
    user = request.user

    if user.profile.in_company(company.pk) and (user.profile.is_manager() or user.profile.is_agent()):
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
    else:
        return redirect(reverse('tables:index'))


@login_required
def client_delete(request, company_pk, client_pk):
    company = get_object_or_404(Company, pk=company_pk)
    client = get_object_or_404(Client, company=company, pk=client_pk)
    user = request.user
    data = dict()

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            client.delete()
            data['form_is_valid'] = True
        else:
            context = {
                'client': client,
                'company': company,
            }
            data['html_form'] = render_to_string('tables/client/client_delete_form.html', context, request=request)
        return JsonResponse(data)
    return redirect(reverse('tables:index'))


@login_required
def clients_delete(request, company_pk):
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
            Client.objects.filter(pk__in=cleaned_ids, company=company).delete()
            data['form_is_valid'] = True
        return JsonResponse(data)
    else:
        return redirect(reverse('tables:index'))
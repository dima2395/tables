from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from ..models import Company
from ..forms import CompanyForm

#is used for setting active menu item
@login_required
def company(request, pk):
    return HttpResponse('LOL')

@login_required
def company_create(request):
    form = CompanyForm(request.POST or None)
    user = request.user
    if user.profile.is_owner and user.company_set.count() == 0:
        if request.method == 'POST':
            if form.is_valid():
                company = form.save(commit=False)
                company.owner = user
                company.save()
                # messages.success(request, 'Компания успешно создана.')
                return redirect(reverse('tables:warehouses', kwargs={'company_pk': company.pk}))
                #return redirect to company page
        return render(request, 'tables/company/company_create.html', {'form': form})
    return redirect(reverse('tables:index'))


@login_required
def company_edit(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)
    form = CompanyForm(request.POST or None, instance=company)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Изменения сохранены успешно.')
                return redirect(reverse('tables:company-edit', kwargs={'company_pk': company.pk}))
            except:
                messages.error(request, 'Что-то пошло не так, попробуйте ещё раз.')


        return render(request, 'tables/company/company_edit.html', {'form': form, 'company': company})
    else:
        return redirect(reverse('tables:index'))


@login_required
def company_delete(request, company_pk):
    user = request.user
    company = get_object_or_404(Company, pk=company_pk)

    if user.profile.in_company(company.pk) and user.profile.is_manager():
        if request.method == 'POST':
            company.delete()
            return redirect(reverse('tables:index')) 
    else:
        return redirect(reverse('tables:index'))
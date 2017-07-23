from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib import messages
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
from django.shortcuts import render


def index(request):
    user = request.user
    context = {}
    if user.is_authenticated():
        company = user.profile.get_companies().first()
        context['company'] = company

    return render(request, 'tables/index.html', context)
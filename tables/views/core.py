from django.shortcuts import render


def index(request):
    company = request.user.profile.get_companies().first()

    return render(request, 'tables/index.html', {'company': company})
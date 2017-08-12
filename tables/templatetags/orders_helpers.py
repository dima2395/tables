
from django import template
from tables.models import Order


register = template.Library()

@register.simple_tag(takes_context=True)
def get_orders_count(context, filtered=""):
    user = context['user']
    company = context['company']

    if filtered:
        orders = Order.objects.filter(company=company, status=filtered)
    else:
        orders = Order.objects.filter(company=company)

    if user.profile.is_agent():
        orders = orders.filter(created_by=user)

    return orders.count()
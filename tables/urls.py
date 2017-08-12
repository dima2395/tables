from django.conf.urls import url
from .views import core, company, warehouse, product, employee, client, service, order

app_name = 'tables'

urlpatterns = [
    url(r'^$', core.index, name="index"),




    url(r'^company/create/$', company.company_create, name='company-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/$', company.company, name='company'),
    url(r'^company/(?P<company_pk>[0-9]+)/edit/$', company.company_edit, name='company-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/delete/$', company.company_delete, name='company-delete'),



    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/create/$', warehouse.warehouse_create, name='warehouse-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/edit/$', warehouse.warehouse_edit, name='warehouse-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/delete/$', warehouse.warehouse_delete, name='warehouse-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouses/$', warehouse.warehouses, name='warehouses'),



    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/create/$', product.product_create, name='product-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/(?P<product_pk>[0-9]+)/edit/$', product.product_edit, name='product-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/(?P<product_pk>[0-9]+)/delete/$', product.product_delete, name='product-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/products/delete/$', product.products_delete, name='products-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/products/$', product.products, name='products'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/products/json/$',product.products_json, name="products-json"),



    url(r'^company/(?P<company_pk>[0-9]+)/employee/create/$', employee.employee_create, name='employee-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/employee/(?P<employee_pk>[0-9]+)/edit/$', employee.employee_edit, name='employee-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/employee/(?P<employee_pk>[0-9]+)/change-password/$', employee.change_password, name='employee-change-password'),
    url(r'^company/(?P<company_pk>[0-9]+)/employee/(?P<employee_pk>[0-9]+)/delete/$', employee.employee_delete, name='employee-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/employees/delete$', employee.employees_delete, name='employees-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/employees/$', employee.employees, name='employees'),
    url(r'^company/(?P<company_pk>[0-9]+)/employees/json$', employee.employees_json, name='employees-json'),



    url(r'company/(?P<company_pk>[0-9]+)/client/create/$', client.client_create, name='client-create'),
    url(r'company/(?P<company_pk>[0-9]+)/client/(?P<client_pk>[0-9]+)/edit/$', client.client_edit, name='client-edit'),
    url(r'company/(?P<company_pk>[0-9]+)/client/(?P<client_pk>[0-9]+)/delete/$', client.client_delete, name='client-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/clients/delete/$', client.clients_delete, name='clients-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/clients/$', client.clients, name='clients'),
    url(r'company/(?P<company_pk>[0-9]+)/clients/json/$', client.clients_json, name='clients-json'),



    url(r'company/(?P<company_pk>[0-9]+)/service/create/$', service.service_create, name='service-create'),
    url(r'company/(?P<company_pk>[0-9]+)/service/(?P<service_pk>[0-9]+)/edit/$', service.service_edit, name='service-edit'),
    url(r'company/(?P<company_pk>[0-9]+)/service/(?P<service_pk>[0-9]+)/delete/$', service.service_delete, name='service-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/services/delete/$', service.services_delete, name='services-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/services/$', service.services, name='services'),
    url(r'company/(?P<company_pk>[0-9]+)/services/json/$', service.services_json, name='services-json'),



    url(r'company/(?P<company_pk>[0-9]+)/order/create/$', order.order_create, name='order-create'),
    url(r'company/(?P<company_pk>[0-9]+)/order/(?P<order_pk>[0-9]+)/edit/$', order.order_edit, name='order-edit'),
    url(r'company/(?P<company_pk>[0-9]+)/order/(?P<order_pk>[0-9]+)/delete/$', order.order_delete, name='order-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/delete/$', order.orders_delete, name='orders-delete'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/$', order.orders, name='orders'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/json/$', order.orders_json, name='orders-json'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/processing/$', order.orders_processing, name='orders-processing'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/json/processing/$', order.orders_processing_json, name='orders-processing-json'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/completed/$', order.orders_completed, name='orders-completed'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/json/completed/$', order.orders_completed_json, name='orders-completed-json'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/suspended/$', order.orders_suspended, name='orders-suspended'),
    url(r'company/(?P<company_pk>[0-9]+)/orders/json/suspended/$', order.orders_suspended_json, name='orders-suspended-json'),

]

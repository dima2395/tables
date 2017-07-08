from django.conf.urls import url
from tables import views

app_name = 'tables'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    # url(r'^table/(?P<pk>[0-9]+)/$', views.detail, name="detail"),
    # url(r'^products/',views.products, name="products"),
    # url(r'^json/products$',views.products_json, name="products-json"),
    # url(r'^product/create/$', views.product_create, name="product-create"),
    # url(r'^product/(?P<pk>[0-9]+)/edit/$', views.product_edit, name='product-edit'),
    # url(r'^product/(?P<pk>[0-9]+)/delete/$', views.product_delete, name='product-delete'),
    url(r'^company/create/$', views.company_create, name='company-create'),
    url(r'^company/(?P<pk>[0-9]+)/$', views.company, name='company'),
    url(r'^company/(?P<pk>[0-9]+)/edit/$', views.company_edit, name='company-edit'),
    url(r'^company/(?P<pk>[0-9]+)/delete/$', views.company_delete, name='company-delete'),


    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/create/$', views.warehouse_create, name='warehouse-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/edit/$', views.warehouse_edit, name='warehouse-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/delete/$', views.warehouse_delete, name='warehouse-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouses/$', views.warehouses, name='warehouses'),


    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/create/$', views.product_create, name='product-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/(?P<product_pk>[0-9]+)/edit/$', views.product_edit, name='product-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/product/(?P<product_pk>[0-9]+)/delete/$', views.product_delete, name='product-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/products/$', views.products, name='products'),
    url(r'^company/(?P<company_pk>[0-9]+)/warehouse/(?P<warehouse_pk>[0-9]+)/products/json/$',views.products_json, name="products-json"),


    url(r'^company/(?P<company_pk>[0-9]+)/employee/create/$', views.employee_create, name='employee-create'),
    url(r'^company/(?P<company_pk>[0-9]+)/employee/(?P<employee_pk>[0-9]+)/edit/$', views.employee_edit, name='employee-edit'),
    url(r'^company/(?P<company_pk>[0-9]+)/employee/(?P<employee_pk>[0-9]+)/delete/$', views.employee_delete, name='employee-delete'),
    url(r'^company/(?P<company_pk>[0-9]+)/employees/$', views.employees, name='employees'),

]

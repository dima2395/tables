from django.conf.urls import url, include
from accounts import views


app_name = 'accounts'

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uid64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^profile/(?P<user_pk>[0-9]+)/edit/$', views.profile_edit, name='profile-edit'),
    url(r'^password/change/$', views.password_change, name='password-change')

]
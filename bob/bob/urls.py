"""bob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from school.views import *
from stronghold.decorators import public
from django.views.generic import RedirectView
#from django.conf import settings

urlpatterns = [
    #url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^user/login/$',  public(login),  name='login'),
    url(r'^user/logout/$',  public(logout),  {'next_page': '/school/'}, name='logout'),
    url(r'^user/password/reset/$', public(password_reset), {'post_reset_redirect' : '/user/password/reset/done/'}, name="password_reset"),
    url(r'^user/password/reset/done/$', public(password_reset_done), name='password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', public(password_reset_confirm), {'post_reset_redirect' : '/user/password/done/'}, name="password_reset_confirm"),
    url(r'^user/password/done/$', public(password_reset_complete)),
    url(r'^admin/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/school/'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^accounts/login/$', public(RedirectView.as_view(url='/user/login/'))),
    url(r'^school/', include('school.urls')),
    url(r'^report_builder/', include('report_builder.urls')) ,
    url(r'^$', public(RedirectView.as_view(url='/school/'))),
    url(r'^impersonate/', include('impersonate.urls')),
]

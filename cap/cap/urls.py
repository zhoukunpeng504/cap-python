# coding:utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from cap import settings
import core_api
import api
import views
import os

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'cap.views.home', name='home'),
                       # url(r'^cap/', include('cap.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       (r"^robots\.txt$",
                        lambda request: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
                       # robots
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r"^login/$", login, {"template_name": "login.html"}),
                       url(r"^logout/$", logout, {"next_page": "/"}),
                       # url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                       #     {'document_root': settings.STATICFILES_DIRS[0], 'show_indexes': settings.DEBUG}),
                       # Uncomment the next line to enable the admin:
                       #url(r"^$", "cap.views.home"),
                       url(r'^admin/', include(admin.site.urls)),  # admin页面
                       url(r"^core_api/",include(core_api.site.urls)), # core_api
                       url(r"^environ",lambda x:HttpResponse(str(os.environ))),
                       url(r"^zhou",lambda x:HttpResponse(str(getattr(os,'zhou')))),
                       url(r"^api/",include(api.site.urls)),
                       (r"^(?P<path>.*)$",views.front_view),
                       )

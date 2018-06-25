#coding:utf-8
__author__ = 'Administrator'
from django.http import  HttpResponse,HttpResponseRedirect
from django.views.static import serve
from django.conf import  settings
import os



def front_view(request, path):
    if not path:
        path = "/"
    if path[0] != "/":
        path = "/" + path
    if path.endswith("/"):
        return HttpResponseRedirect(path+"index.html")
    else:
        real_file_path = os.path.join("/front", "." + path)
        real_file_path = os.path.abspath(real_file_path)
        try:
            return serve(request, real_file_path, settings.STATICFILES_DIRS[0])
        except:
            if path.startswith("/static/"):
                try:
                    serve(request, path.replace("/static/",''), settings.STATICFILES_DIRS[0])
                except:
                    return  HttpResponse("404!%s"%real_file_path,status=404)
            else:
                return HttpResponse("404!%s" % real_file_path, status=404)










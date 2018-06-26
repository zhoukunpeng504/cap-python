# coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/10/18.
# ---------------------------------
from django.conf.urls import patterns,url
from views import *
import  sys


class Api(object):
    def __init__(self, name="api", app_name="api"):
        self.namespace = name
        self.app_name = app_name

    def get_urls(self):
        urlpatterns = patterns('',
                               (r"^meta_test", meta_test),
                               (r"^api_gateway", api_gateway),
                               (r"^api_document", api_document),
                                (r"^get_session_key",get_session_key),
            )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = Api()

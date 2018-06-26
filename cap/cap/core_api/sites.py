# coding:utf-8
# write  by  zhou

from django.conf.urls import include, url, patterns


class CoreApi(object):
    def __init__(self, name="core_api", app_name="core_api"):
        self.name = name
        self.app_name = app_name

    def get_urls(self):
        return patterns("cap.core_api",
                        url(r"^work_heartbeat/$", "views.worker.worker_heartbeat"),

                        )

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

    @urls.setter
    def urls(self, value):
        pass

    @urls.deleter
    def urls(self):
        pass


site = CoreApi()

#coding:utf-8
# write  by  zhou


# def get_manage_dir():
#     return  cap.__path__
# sys.path.append(get_manage_dir()[0])
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cap.settings")
# from django.core.handlers.wsgi import WSGIHandler
# application = WSGIHandler()
# resource = WSGIResource(reactor, reactor.getThreadPool(), application)
# ui_service=TCPServer(int(config["uiport"]),server.Site(resource),interface=config["host"])
# ui_service.setServiceParent(s)
import re
def get_mount_info():
    import psutil
    result = []
    for info in psutil.disk_partitions():
        dir = info.mountpoint
        result.append(psutil.disk_usage(dir))
    return result

print get_mount_info()

class Test:
    def __deepcopy__(self, memodict):
        print "deep copy"
        return 123



import copy
print  copy.deepcopy(Test())
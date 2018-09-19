# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/7/20.
# ---------------------------------
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker, MultiService,Application
from twisted.application.internet import TCPServer
import sys
from twisted.web import server
import os
import netifaces
from twisted.python.logfile import DailyLogFile,LogFile

reload(sys)
sys.setdefaultencoding("utf-8")


def get_local_ipaddr():
    results = []
    for i in netifaces.interfaces():
        info = netifaces.ifaddresses(i)
        if netifaces.AF_INET not in info:
            continue
        _ = info[netifaces.AF_INET][0]['addr']
        if _ != "127.0.0.1":
            results.append(_)
    return results


def option_master_valid(val):
    return val


option_master_valid.coerceDoc = "主节点的IP地址, 比如 192.168.11.1"


def option_host_valid(val):
    if val in get_local_ipaddr():
        return val
    else:
        raise Exception("%s 不是一个可用的地址, 本机所有可绑定的地址如下 %s" % (val, ",".join(get_local_ipaddr())))


option_host_valid.coerceDoc = "服务绑定的IP地址，本机所有可绑定的IP地址如下 %s" % (
    ",".join(get_local_ipaddr()))

def option_work_dir_valid(val):
    if val[0]!='/':
        raise Exception("%s 必须是一个绝对路径,比如 /data/crondeamon_work ")
    try:
        assert os.path.exists(val)
    except:
        raise Exception("%s 不是一个可用的目录,请检查目录是否存在及权限是否正确！"%val)
    return val


option_work_dir_valid.coerceDoc = "服务的工作目录"

class Options(usage.Options):
    optParameters = [
        ["master", "m", None, None, option_master_valid],
        ["host", "h", None, None, option_host_valid],
        ["work_dir","w",None,None,option_work_dir_valid]
    ]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "cap-worker"
    description = "cap-worker服务，用于cap系统。"
    options = Options

    def makeService(self, options):
        config = options
        s = MultiService()

        from cap_twisted import service as mainrpc
        serverfactory = server.Site(mainrpc.MainRpc(config["master"],config["work_dir"]))
        slave_service = TCPServer(9913, serverfactory, interface=config["host"])
        slave_service.setServiceParent(s)
        return s


serviceMaker = MyServiceMaker()


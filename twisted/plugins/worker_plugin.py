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


option_master_valid.coerceDoc = "the master ip, example 192.168.11.1"


def option_host_valid(val):
    if val in get_local_ipaddr():
        return val
    else:
        raise Exception("%s not a valid address, it not in %s" % (val, ",".join(get_local_ipaddr())))


option_host_valid.coerceDoc = "address to bind, all valid address in this machine is %s" % (
    ",".join(get_local_ipaddr()))

def option_work_dir_valid(val):
    if val[0]!='/':
        raise Exception("%s must be a absolute path,example: /data/crondeamon_work")
    try:
        assert os.path.exists(val)
    except:
        raise Exception("%s not a valid dir,please check the dir is existed or the dir permission is right"%val)
    return val


option_work_dir_valid.coerceDoc = "the dir for work. it is be used to save the code file"

class Options(usage.Options):
    optParameters = [
        ["master", "m", None, None, option_master_valid],
        ["host", "h", None, None, option_host_valid],
        ["work_dir","w",None,None,option_work_dir_valid]
    ]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "cap-worker"
    description = "cap worker role ..."
    options = Options

    def makeService(self, options):
        config = options
        s = MultiService()

        from crondeamon.worker import service as mainrpc
        serverfactory = server.Site(mainrpc.MainRpc(config["master"],config["work_dir"]))
        slave_service = TCPServer(9913, serverfactory, interface=config["host"])
        slave_service.setServiceParent(s)
        return s


serviceMaker = MyServiceMaker()


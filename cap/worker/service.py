# coding:utf-8
__author__ = 'zhoukunpeng'
# --------------------------------
# Created by zhoukunpeng  on 2015/6/4.
# ---------------------------------
from twisted.web import xmlrpc
from twisted.internet import reactor, task, defer, threads
from txscheduling.cron import CronSchedule
from txscheduling.task import ScheduledCall
from twisted.internet import protocol, error
import psutil
import sys
import cloudpickle
import base64
import os
from twisted.web.client import getPage
import urllib
import traceback
from django.conf import settings


settings.configure()

reactor.suggestThreadPoolSize(500)  # 线程池改为500， 防止线程占满
reload(sys)
sys.setdefaultencoding("utf-8")

CRON_BUFF = {}  # CRON 专用全局变量
TASK_BUFF = {}  # TASK 专用全局变量
DEAMON_BUFF = {}
PID_BUFF = {}


def set_time_out(seconds, deferjob):
    "给一个deferjob添加一个超时时间,防止一个xmlrpc运行时间过长。"

    def _handle(deferjob):
        if deferjob.called:
            pass
        else:
            deferjob.cancel()

    seconds = int(seconds)
    reactor.callLater(seconds, _handle, deferjob)
    return True


class ProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, fun, fun_args, fun_kwargs, callback, errback, stdout_callback=None, stderr_callback=None):
        self.pid = None
        self.lastpid = None
        self.running = False
        self.has_end = False
        self.callback = callback
        self.errback = errback
        self.stdout_callback = stdout_callback
        self.stderr_callback = stderr_callback
        try:
            _ = {"fun": fun, "callback": callback, "errback": errback, "args": fun_args, "kwargs": fun_kwargs}
            _ = cloudpickle.dumps(_)
            _ = base64.b64encode(_)
            self.pickle_data = _
        except:
            raise Exception("can not pickle the fun or callback or errback ,please recheck it!")
        else:
            pass

        self.stdout_data = ""
        self.stderr_data = ""

    def run(self):
        reactor.spawnProcess(self, "python", ["python", "worker.py"],
                             env=os.environ, path=os.path.dirname(__file__))
        self.running = True
        self.has_end = False
        self.stdout_data = ""
        self.stderr_data = ""

    def is_run(self):
        return self.running

    def connectionMade(self):
        self.pid = self.transport.pid
        self.running = True
        self.has_end = False
        self.transport.write(self.pickle_data + "\n")

    def outReceived(self, data):
        "stdout data"
        #print "[SUBPROCESS-OUTPUT]:", data
        if len(self.stdout_data) <= 2000:
            self.stdout_data += data
        else:
            pass

    def errReceived(self, data):
        "stderr data"
        #print "[SUBPROCESS-ERRPUT]", data
        if len(self.stderr_data) <= 2000:
            self.stderr_data += data
        else:
            pass

    def processExited(self, reason):
        #print "process exited", [reason], reason
        self.has_end = True
        self.running = False
        is_right = True
        if reason.type == error.ProcessTerminated or isinstance(reason.type, error.ProcessTerminated):
            is_right = False
        else:
            try:
                assert (reason.value.exitCode > 0 or reason.value.exitCode < 0)
                is_right = False
            except:
                pass
        print "is_right", is_right

        if self.stdout_callback:
            _run_in_sub(self.stdout_callback, [self.stdout_data, is_right], {}, 3)
        if self.stderr_callback:
            _run_in_sub(self.stderr_callback, [self.stderr_data, is_right], {}, 3)

    def processEnded(self, reason):
        pass

    def kill(self):
        "杀死进程"
        if self.running:
            _mainprocess = psutil.Process(pid=self.pid)
            childpids = _mainprocess.children(True)
            buff = dict([(k.pid, k.create_time()) for k in childpids])
            #print buff
            self.transport.signalProcess(9)
            for j in childpids:
                try:
                    _process = psutil.Process(j.pid)
                except:
                    pass
                else:
                    if _process.is_running() and j.create_time() == buff[j.pid]:
                        _process.send_signal(9)
        self.running = False
        return True

    def restart(self):
        self.kill()
        self.run()


class Process(object):
    def __init__(self, fun, fun_args, fun_kwargs, callback, errback, stdout_callback=None, stderr_callback=None):
        self.kwargs = locals()
        del self.kwargs["self"]
        self.current_process = None

    def run(self):
        if self.current_process:
            self.current_process.kill()
        self.current_process = ProcessProtocol(**self.kwargs)
        self.current_process.run()

    def kill(self):
        if self.current_process:
            self.current_process.kill()

    def restart(self):
        self.run()

    def is_run(self):
        if self.current_process:
            return self.current_process.is_run()
        else:
            return False


def _run_in_sub(fun, fun_args, fun_kwargs, timeout=None):
    p = Process(fun, fun_args, fun_kwargs, callback=lambda x: None, errback=lambda x: None)
    p.run()
    if timeout:
        reactor.callLater(timeout, p.kill)


def run_in_process(fun, fun_args=[], fun_kwargs={}, timeout=None):
    p = Process(fun, fun_args, fun_kwargs, callback=lambda *x: None, errback=lambda *x: None)
    p.run()
    if timeout:
        reactor.callLater(timeout, p.kill)


MASTER_IP = ''
WORK_DIR = ''


class MainRpc(xmlrpc.XMLRPC):

    def __init__(self, master_ip, work_dir):
        xmlrpc.XMLRPC.__init__(self, False, False)
        global MASTER_IP, WORK_DIR
        self.work_dir = work_dir
        self.maser_ip = master_ip
        WORK_DIR = work_dir
        MASTER_IP = master_ip
        self.cache = {}

    def xmlrpc_cache_set(self,key,value):
        self.cache[key] = value
        return True

    def xmlrpc_cache_get(self,key):
        return self.cache.get(key,None)

    def xmlrpc_cache_del(self,key):
        try:
            del self.cache[key]
        except:
            pass

    def valid_cronrule(self, rule):
        rule = rule.strip()
        try:
            CronSchedule(rule)
        except:
            return False, "时间规则不符合要求"
        else:
            return True

    def xmlrpc_ping(self, *args, **kwargs):
        return True

    def xmlrpc_cron_get(self, key):
        if CRON_BUFF.has_key(key):
            return True
        else:
            return False

    def xmlrpc_cron_del(self, key):
        print "cron server _cron del"
        if CRON_BUFF.has_key(key):
            CRON_BUFF[key][0].stop()
            CRON_BUFF[key][1].kill()
            del CRON_BUFF[key]
            return True
        else:
            return True

    def xmlrpc_cron_is_running(self, key):
        if CRON_BUFF.has_key(key):
            return CRON_BUFF[key][1].is_run()
        else:
            return False

    def xmlrpc_cron_set(self, key, cron_mode, picked_function, picked_callback, picked_errback, stdout_callback,
                        stderr_callback):
        print "cron server _ cron set"
        try:
            self.xmlrpc_cron_del(key)
            if self.valid_cronrule(cron_mode):
                pass
            else:
                raise Exception("cron时间规则不符合要求")
            try:
                target = cloudpickle.loads(picked_function.data)
            except:
                traceback.print_exc()
                raise Exception("目标函数picked反序列化失败!")
            try:
                callback = cloudpickle.loads(picked_callback.data)
            except:
                raise Exception("success回调函数picked反序列化失败!")
            try:
                errback = cloudpickle.loads(picked_errback.data)
            except:
                raise Exception("error回调函数picked反序列化失败!")
            if stdout_callback:
                try:
                    stdout_callback = cloudpickle.loads(stdout_callback.data)
                except:
                    raise Exception("stdout回调函数picked反序列化失败!")
            else:
                stdout_callback = None
            if stderr_callback:
                try:
                    stderr_callback = cloudpickle.loads(stderr_callback.data)
                except:
                    raise Exception("stderr回调函数picked反序列化失败!")
            else:
                stderr_callback = None
            cron = CronSchedule(cron_mode)

            _process = Process(target, [], {}, callback, errback, stdout_callback, stderr_callback)
            _task = ScheduledCall(_process.restart)
            _task.start(cron)
            CRON_BUFF[key] = (_task, _process)
        except Exception as e:
            traceback.print_exc()
            return False, str(e)
        else:
            return True

    def xmlrpc_cron_run_now(self, key):
        result = self.xmlrpc_cron_get(key)
        if result:
            CRON_BUFF[key][1].restart()
            return True
        else:
            return False, "此cron不存在！"

    def xmlrpc_task_set(self, key, picked_function, picked_callback, picked_errback, stdout_callback,
                        stderr_callback, timeoutback=None, timeout=60):
        print "task set"
        try:
            self.xmlrpc_task_del(key)
            try:
                target = cloudpickle.loads(picked_function.data)
            except:
                traceback.print_exc()
                raise Exception("目标函数picked反序列化失败!")
            try:
                callback = cloudpickle.loads(picked_callback.data)
            except:
                traceback.print_exc()
                raise Exception("success回调函数picked反序列化失败!")
            try:
                errback = cloudpickle.loads(picked_errback.data)
            except:
                raise Exception("error回调函数picked反序列化失败!")
            if stdout_callback:
                try:
                    stdout_callback = cloudpickle.loads(stdout_callback.data)
                except:
                    raise Exception("stdout回调函数picked反序列化失败!")
            else:
                stdout_callback = None
            if stderr_callback:
                try:
                    stderr_callback = cloudpickle.loads(stderr_callback.data)
                except:
                    raise Exception("stderr回调函数picked反序列化失败!")
            else:
                stderr_callback = None
            _process = Process(target, [], {}, callback, errback, stdout_callback, stderr_callback)
            _process.run()
            if timeout:
                def _():
                    if _process.is_run() and timeoutback:
                        run_in_process(cloudpickle.loads(timeoutback.data))

                reactor.callLater(timeout, _)
            TASK_BUFF[key] = _process
        except Exception as e:
            traceback.print_exc()
            print str(e)
            return False, str(e)
        else:
            return True

    def xmlrpc_task_del(self, key):
        if TASK_BUFF.has_key(key):
            TASK_BUFF[key].kill()
            del TASK_BUFF[key]
            return True
        else:
            return True

    def xmlrpc_task_is_running(self, key):
        if TASK_BUFF.has_key(key):
            return TASK_BUFF[key].is_run()
        else:
            return False

    def xmlrpc_deamon_set(self, key, picked_function, picked_callback, picked_errback, stdout_callback,
                          stderr_callback):
        print "task set"
        try:
            self.xmlrpc_deamon_del(key)
            try:
                target = cloudpickle.loads(picked_function.data)
            except:
                traceback.print_exc()
                raise Exception("目标函数picked反序列化失败!")
            try:
                callback = cloudpickle.loads(picked_callback.data)
            except:
                traceback.print_exc()
                raise Exception("success回调函数picked反序列化失败!")
            try:
                errback = cloudpickle.loads(picked_errback.data)
            except:
                raise Exception("error回调函数picked反序列化失败!")
            if stdout_callback:
                try:
                    stdout_callback = cloudpickle.loads(stdout_callback.data)
                except:
                    raise Exception("stdout回调函数picked反序列化失败!")
            else:
                stdout_callback = None
            if stderr_callback:
                try:
                    stderr_callback = cloudpickle.loads(stderr_callback.data)
                except:
                    raise Exception("stderr回调函数picked反序列化失败!")
            else:
                stderr_callback = None
            _process = Process(target, [], {}, callback, errback, stdout_callback, stderr_callback)
            _process.run()
            print "task process run"
            DEAMON_BUFF[key] = _process
        except Exception as e:
            traceback.print_exc()
            print str(e)
            return False, str(e)
        else:
            return True

    def xmlrpc_deamon_get(self, key):
        if DEAMON_BUFF.has_key(key):
            return True
        else:
            return False

    def xmlrpc_deamon_del(self, key):
        if DEAMON_BUFF.has_key(key):
            DEAMON_BUFF[key].kill()
            del DEAMON_BUFF[key]
            return True
        else:
            return True

    def xmlrpc_deamon_is_running(self, key):
        if DEAMON_BUFF.has_key(key):
            return DEAMON_BUFF[key].is_run()
        else:
            return False

    def xmlrpc_deamon_run_now(self, key):
        result = self.xmlrpc_deamon_get(key)
        if result:
            DEAMON_BUFF[key].restart()
        else:
            return False, "此后台任务不存在！"


num = 0


def check_deamon_run():
    for i, j in DEAMON_BUFF.items():
        if j.is_run():
            pass
        else:
            j.run()
    reactor.callLater(30, check_deamon_run)

reactor.callLater(5, check_deamon_run)

def heartbeat():
    global num
    num += 1
    _defer = getPage(
        "http://%s:9912/core_api/work_heartbeat/?num=%s&work_dir=%s" % (MASTER_IP, num, urllib.quote(WORK_DIR)))

    def callback(*args):
        print "work_heartbeat success!"

    def errback(*args):
        print "work_heartbeat failed! master maybe down!!"
    _defer.addCallback(callback)
    _defer.addErrback(errback)
    reactor.callLater(3, heartbeat)

reactor.callLater(1, heartbeat)



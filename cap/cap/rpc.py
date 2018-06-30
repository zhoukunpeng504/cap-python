#coding:utf-8
# write  by  zhou

#coding:utf-8
# write  by  zhou



class Ping(object):

    def __init__(self, ip):
        import xmlrpclib
        self.ip = ip
        self.server = xmlrpclib.ServerProxy("http://%s:9913" % ip, allow_none=True)
    def ping(self):
        try:
            self.server.ping()
            return True
        except:
            raise Exception("[%s]:Exception:%s" % (self.ip, "该节点已经离线"))


class Cache(object):

    def __init__(self, ip):
        import xmlrpclib
        self.ip = ip
        self.server = xmlrpclib.ServerProxy("http://%s:9913" % ip, allow_none=True)

    def set(self,key,value):
        try:
            self.server.cache_set(key,value)
            return True
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def get(self,key):
        try:
            return self.server.cache_get(key)
        except  Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def delete(self,key):
        try:
            return self.server.cache_del(key)
        except  Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


class Cron(object):
    def __init__(self,ip):
        import xmlrpclib
        self.ip = ip
        self.server = xmlrpclib.ServerProxy("http://%s:9913"%ip,allow_none=True)

    def get(self,key):
        try:
            result = self.server.cron_get(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


    def set(self,key,cron_mode,cron_function,cron_callback,cron_errback,stdout_callback,
                   stderr_callback):
        import xmlrpclib,cloudpickle
        #cron_function.__module__ = "__main__"
        cron_function = cloudpickle.dumps(cron_function)
        cron_callback = cloudpickle.dumps(cron_callback)
        cron_errback = cloudpickle.dumps(cron_errback)
        stdout_callback = cloudpickle.dumps(stdout_callback)
        stderr_callback = cloudpickle.dumps(stderr_callback)
        try:
            result = self.server.cron_set(key,cron_mode,xmlrpclib.Binary(cron_function),
                                    xmlrpclib.Binary(cron_callback),xmlrpclib.Binary(cron_errback),
                                    xmlrpclib.Binary(stdout_callback),xmlrpclib.Binary(stderr_callback))
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def delete(self,key):
        try:
            result = self.server.cron_del(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def is_running(self,key):
        try:
            result = self.server.cron_is_running(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def run_now(self,key):
        try:
            result = self.server.cron_run_now(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


class Deamon(object):
    def __init__(self,ip):
        import xmlrpclib
        self.ip = ip
        self.server = xmlrpclib.ServerProxy("http://%s:9913"%ip,allow_none=True)

    def set(self,key,function,callback,errback,stdout_callback,
                   stderr_callback):
        import xmlrpclib,cloudpickle
        function=cloudpickle.dumps(function)
        callback=cloudpickle.dumps(callback)
        errback=cloudpickle.dumps(errback)
        stdout_callback=cloudpickle.dumps(stdout_callback)
        stderr_callback=cloudpickle.dumps(stderr_callback)
        try:
            result = self.server.deamon_set(key,xmlrpclib.Binary(function),
                                    xmlrpclib.Binary(callback),xmlrpclib.Binary(errback),
                                    xmlrpclib.Binary(stdout_callback),xmlrpclib.Binary(stderr_callback))
            if isinstance(result, (list, tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e:
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


    def delete(self,key):
        try:
            result = self.server.deamon_del(key)
            if isinstance(result, (list, tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e:
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


    def is_running(self,key):
        try:
            result = self.server.deamon_is_running(key)
            if isinstance(result, (list, tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e:
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def get(self,key):
        try:
            result = self.server.deamon_get(key)
            if isinstance(result, (list, tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e:
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))


class Task(object):
    def __init__(self, ip):
        import xmlrpclib
        self.ip  = ip
        self.server = xmlrpclib.ServerProxy("http://%s:9913" % ip, allow_none=True)

    def set(self, key, function, callback, errback, stdout_callback,
            stderr_callback,timeout_callback=lambda *x:None,timeout=60):
        import  xmlrpclib,cloudpickle
        function = cloudpickle.dumps(function)
        callback = cloudpickle.dumps(callback)
        errback = cloudpickle.dumps(errback)
        stdout_callback = cloudpickle.dumps(stdout_callback)
        stderr_callback = cloudpickle.dumps(stderr_callback)
        timeout_callback = cloudpickle.dumps(timeout_callback)
        try:
            result = self.server.task_set(key, xmlrpclib.Binary(function),
                                      xmlrpclib.Binary(callback), xmlrpclib.Binary(errback),
                                      xmlrpclib.Binary(stdout_callback), xmlrpclib.Binary(stderr_callback),
                                      xmlrpclib.Binary(timeout_callback),timeout)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def delete(self, key):
        try:
            result = self.server.task_del(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def is_running(self, key):
        try:
            result = self.server.task_is_running(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

    def get(self, key):
        try:
            result = self.server.task_get(key)
            if isinstance(result,(list,tuple)):
                raise Exception(result[1])
            else:
                return result
        except Exception as e :
            raise Exception("[%s]:Exception:%s" % (self.ip, str(e)))

if __name__ == "__main__":
    import time
    task = Task("192.168.8.185")
    def test():
        import redis
        conn=redis.Redis("192.168.8.185",6379)
        conn.incr("testabc",10)


    _task = Task("192.168.8.185")

    def incr():
        import redis
        conn=redis.Redis("192.168.8.185",6379)
        conn.incr("zhou",10)
        import time
        time.sleep(2)
        _task = Task("192.168.8.185")
        _task.set("testabcd",test,lambda x:None,lambda x:None,lambda *x:None,lambda *x:None)

    # deamon.set("test",incr,lambda x:None,lambda x:None,lambda *x:None,lambda *x:None)
    # while 1:
    #     time.sleep(0.1)
    #     print deamon.is_running("test")
    task.set("test",incr,lambda x:None,lambda x:None,lambda *x:None,lambda *x:None)
    while 1:
        time.sleep(0.3)
        print task.is_running("test")
    # print cron.set("test","* * * * *",incr,lambda X:None,lambda x:None,lambda *x:None,lambda *x:None)
    # print cron.get("test")
    # import  time
    # while 1:
    #     time.sleep(1)
    #     print cron.is_running("test")
    #     print cron.is_running("test")


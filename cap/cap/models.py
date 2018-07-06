# coding:utf-8
__author__ = 'python'
from django.contrib.auth.models import User
from django.db import models
from cap import  settings
import time
from rpc import *



class Group(models.Model):
    "分组"
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='', unique=True)
    addtime = models.PositiveIntegerField(default=lambda: int(time.time()))


if Group.objects.all().count() == 0:
    group = Group(name="默认")
    group.save()


class Worker(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=100, db_index=True, unique=True)
    addtime = models.PositiveIntegerField(default=lambda: int(time.time()))
    heartbeat = models.PositiveIntegerField(default=0)
    work_dir = models.CharField(max_length=50, default='')
    total_cpu = models.PositiveIntegerField(default=0)      # cpu信息（个）
    total_mem = models.PositiveIntegerField(default=0)      # 内存信息 （MB）
    platform = models.CharField(max_length=300)             # 系统信息


    @classmethod
    def worker_heartbeat(cls, ip, work_dir):
        try:
            _ = cls.objects.get(ip=ip)
        except:
            _ = cls(ip=ip, addtime=int(time.time()), heartbeat=int(time.time()))
            _.save()
        _.heartbeat = int(time.time())
        _.work_dir = work_dir
        _.save()
        return _

    def is_alive(self):
        if time.time() - self.heartbeat <= 6:
            return True
        else:
            try:
                Ping(self.ip).ping()
            except:
                return False
            else:
                return True

    def cpu_mem_load_now(self):
        if self.is_alive():
            try:
                _ = WorkerCpuMemLog.objects.filter(work_id=self.id).order_by("-id")[0]
            except:
                return [None,None]
            return [_.cpu_percent,_.mem_percent]
        else:
            return [None,None]

    def cpu_mem_load_history(self):
        if self.is_alive():
            info = WorkerCpuMemLog.objects.filter(work_id=self.id).order_by("-id")[:300]
            result = []
            for i in info:
                result.append({"addtime":i.addtime,"cpu_percent":i.cpu_percent,
                               "mem_percent":i.mem_percent})
            result.reverse()
            return result

    @property
    def mysql_config(self):
        return {"host": settings.DATABASES["default"]["HOST"],
                "port": int(settings.DATABASES["default"]["PORT"]),
                'user': settings.DATABASES["default"]["USER"],
                "passwd": settings.DATABASES["default"]["PASSWORD"],
                "db": settings.DATABASES["default"]["NAME"],
                "charset": "utf8"}

    def pure_init(self):
        def monitor(work_id=self.id,mysql_config=self.mysql_config):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid
            import psutil,platform
            total_cpu = psutil.cpu_count()
            memory_info = psutil.virtual_memory()
            total_memory = int(memory_info.total/(1024*1024))
            used_cpu_percent = psutil.cpu_percent(3)
            used_memory = memory_info.used/(1024*1024)
            used_memory_percent = int(used_memory/float(total_memory)*100)
            platform = platform.platform()
            run_sql(mysql_config,"update cap_worker set platform=%s,total_cpu=%s,total_mem=%s where id=%s",(platform,
                                                                                                    int(total_cpu),
                                                                                                    int(total_memory),
                                                                                                    work_id))
            run_sql(mysql_config,"insert into cap_worker_cpumem_log(addtime,cpu_percent,mem_percent,work_id) \
                                  values(unix_timestamp(now()),%s,%s,%s) ",(used_cpu_percent,used_memory_percent,
                                                                            work_id))
            run_sql(mysql_config,"delete from cap_worker_cpumem_log where addtime < unix_timestamp(now())-86400*7")
        cron = Cron(self.ip)
        cron.set("%s-cpu_mem_log"%self.ip,"* * * * *",monitor,lambda *x:None,lambda *x:None,lambda *x:None,
                 lambda *x:None)
            

class WorkerCpuMemLog(models.Model):
    "worker节点cpu内存信息"
    id = models.AutoField(primary_key=True)
    work_id = models.PositiveIntegerField(default=0)
    addtime = models.PositiveIntegerField(default=lambda:int(time.time()))
    cpu_percent = models.PositiveIntegerField(default=0)
    mem_percent = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "cap_worker_cpumem_log"


# class WorkerPartitionLog(models.Model):
#     "worker节点磁盘信息"
#     pass

class Repo(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.PositiveIntegerField(default=0)  # 1 svn  2 git
    repo_url = models.CharField(default='', max_length=200, db_index=True, unique=True)
    user = models.CharField(default='', max_length=50)
    password = models.CharField(default='', max_length=50)
    addtime = models.IntegerField(default=lambda: int(time.time()))

    @classmethod
    def upsert(cls, repo_url, type):
        if type == 2:
            if not repo_url.starswith("https://"):
                raise Exception("git类型的仓库地址必须是https://开头的")
        try:
            cls.objects.get(repo_url=repo_url)
        except:
            _ = cls(type=type, repo_url=repo_url)
            _.save()


class PubLog(models.Model):
    pubid = models.AutoField(primary_key=True)
    target_id = models.PositiveIntegerField(default=0)
    target_type = models.CharField(max_length=20, default='')
    addtime = models.PositiveIntegerField(default=lambda: int(time.time()))
    finishtime = models.PositiveIntegerField(default=0)
    # shell = models.TextField(default='')
    stdout = models.TextField(default='')
    stderr = models.TextField(default='')
    state = models.PositiveIntegerField(default=0)  # 0待执行  1正在执行  2执行超时  3 执行失败  4执行成功

    class Meta:
        db_table = "pub_log"
        
    def get_state(self):
        return {0:"待执行",1:"正在执行",2:"执行超时",3:"执行失败",4:"执行成功"}[self.state]


class CronTask(models.Model):
    "计划任务的抽象"
    tid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, db_index=True, verbose_name="名称")
    worker_id = models.PositiveIntegerField(default=0, verbose_name="worker id")
    addtime = models.IntegerField(verbose_name="创建时间", default=lambda: int(time.time()))
    uptime = models.IntegerField(verbose_name="修改时间",default=lambda :int(time.time()))
    rule = models.CharField(max_length=50, verbose_name="Cron规则")
    status = models.IntegerField(default=0, verbose_name="状态", db_index=True)  # -1 禁用      1  启用   0  待部署  2正在部署  3部署失败
    repo_id = models.PositiveIntegerField(default=0)
    version = models.CharField(verbose_name="版本", default='',max_length=32)
    pre_build = models.CharField(max_length=200, default='')
    info = models.CharField(verbose_name="说明", max_length=300)
    owner = models.CharField(verbose_name="所属人", db_index=True, max_length=300)
    run_cmd = models.CharField(verbose_name="参数", max_length=500)  # 运行参数
    run_times = models.PositiveIntegerField(default=0)
    group_id = models.PositiveIntegerField(default=0)
    runlog_rid = models.PositiveIntegerField(default=0)  # run log id

    class Meta:
        verbose_name = "计划任务"
        verbose_name_plural = "所有计划任务"

    @property
    def worker(self):
        return Worker.objects.get(id=self.worker_id)

    def get_status(self):
        return {-1: "禁用", 1: "启用", 0: "待部署", 2: "正在部署", 3: "部署失败"}[self.status]

    @property
    def group(self):
        return Group.objects.get(id=self.group_id)
    
    @property
    def repo(self):
        repo_id = self.repo_id
        return Repo.objects.get(id=repo_id)

    @property
    def key(self):
        return str(self.tid)

    @property
    def mysql_config(self):
        return {"host": settings.DATABASES["default"]["HOST"],
                "port": int(settings.DATABASES["default"]["PORT"]),
                'user': settings.DATABASES["default"]["USER"],
                "passwd": settings.DATABASES["default"]["PASSWORD"],
                "db": settings.DATABASES["default"]["NAME"],
                "charset": "utf8"}

    def pure_init(self):
        self.__module__ = "__main__"
        if not self.worker.is_alive():
            raise Exception("该节点已经下线!")
        cron = Cron(self.worker.ip)
        if cron.get(self.key):
            cron.delete(self.key)
        publog = PubLog(target_id=self.tid, target_type="cron", state=0)
        publog.save()
        self.status = 0
        self.save()
        def function(pubid=publog.pubid, repo_url=self.repo.repo_url, type=self.repo.type, user=self.repo.user,
                     password=self.repo.password,
                     version=self.version, work_dir=self.worker.work_dir, mysql_config=self.mysql_config,
                     pre_build=self.pre_build,tid=self.tid):
            import os
            import urlparse
            import urllib
            import datetime

            def run_command(shell_cmd):
                import sys, datetime,os
                if sys.getdefaultencoding()!="utf-8":
                    reload(sys)
                    sys.setdefaultencoding("utf-8")
                result = os.system(shell_cmd)
                if result == 0:
                    pass
                else:
                    sys.stderr.write("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                    shell_cmd, result))
                    #sys.stderr.flush()
                    raise Exception("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                   shell_cmd, result))

            def run_sql(mysql_conf, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_conf)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()
            run_sql(mysql_config,"update cap_crontask set status=2 where tid=%s and status=0",(tid,))
            run_sql(mysql_config, "update pub_log set state=1  where pubid=%s", (pubid,))
            print "[%s]开始拉取代码：..." % datetime.datetime.now()
            code_dir = os.path.join(work_dir, "cron", "%s" % tid)
            run_command("rm -rf %s" % code_dir)
            run_command("mkdir -p %s" % code_dir)
            if type == 1:  # svn
                command = "cd %s && svn checkout  -r %s  %s  code_dir --username %s --password %s \
                            --no-auth-cache --non-interactive" % (
                    code_dir, version, repo_url, user, password)
            else:  # git
                url_object = urlparse.urlparse(repo_url)
                if user or password:
                    command = "cd %s && git clone https://%s:%s@%s%s  code_dir  -b  master    && cd  code_dir && git reset \
                      --hard   %s" % (code_dir, urllib.quote(user), urllib.quote(password),
                                      url_object.netloc, url_object.path, version)
                else:
                    command = "cd %s && git clone %s  code_dir  -b  master    && cd  code_dir && git reset \
                                          --hard   %s" % (code_dir, repo_url, version)

            run_command(command)
            print "[%s]拉取代码完成：Success!" % (datetime.datetime.now())
            print "[%s]开始预处理代码:......" % (datetime.datetime.now())
            if pre_build.strip():
                run_command("cd %s/code_dir &&%s"%(code_dir,pre_build))
            print "[%s]预处理代码完成：Success!" % (datetime.datetime.now())

        def callback(_, pubid=publog.pubid, mysql_config=self.mysql_config, ip=self.worker.ip, rule=self.rule,
                     run_function=self.run_function,run_stdout_callback=self.run_stdout_callback,
                     run_stderr_callback=self.run_stderr_callback,tid=self.tid):
            def run_sql(mysql_conf, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_conf)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            run_sql(mysql_config, "update cap_crontask set status=1 where tid=%s and status>=0", (tid,))
            import xmlrpclib,cloudpickle
            server = xmlrpclib.ServerProxy("http://%s:9913"%ip)
            run_function = cloudpickle.dumps(run_function)
            empty_function = cloudpickle.dumps(lambda *x:None)
            run_stdout_callback = cloudpickle.dumps(run_stdout_callback)
            run_stderr_callback = cloudpickle.dumps(run_stderr_callback)
            server.cron_set("%s" % tid, rule, xmlrpclib.Binary(run_function),
                            xmlrpclib.Binary(empty_function),
                            xmlrpclib.Binary(empty_function),
                            xmlrpclib.Binary(run_stdout_callback),
                            xmlrpclib.Binary(run_stderr_callback),
                            )

        def stdout_callback(stdout, is_right, mysql_config=self.mysql_config, pubid=publog.pubid, tid=self.tid):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            if is_right:
                state = 4
            else:
                state = 3
            run_sql(mysql_config, "update pub_log set stdout=%s , finishtime=unix_timestamp(now()) \
                 where pubid=%s ", (stdout, pubid,))
            run_sql(mysql_config, "update pub_log set state=%s  where pubid=%s and \
                state!=2", (state, pubid,))
            if not is_right:
                run_sql(mysql_config, "update cap_crontask set status=%s where tid=%s", (3, tid))

        def stderr_callback(stdout, is_right, mysql_config=self.mysql_config, pubid=publog.pubid, tid=self.tid):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            if is_right:
                state = 4
            else:
                state = 3
            run_sql(mysql_config, "update pub_log set stderr=%s , finishtime=unix_timestamp(now()) \
                             where pubid=%s ", (stdout, pubid,))
            run_sql(mysql_config, "update pub_log set state=%s  where pubid=%s and \
                            state!=2", (state, pubid,))
            if not is_right:
                run_sql(mysql_config, "update cap_crontask set status=%s where tid=%s", (3, tid))

        def timeout_callabck(pubid=publog.pubid, tid=self.tid,mysql_config=self.mysql_config):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            run_sql(mysql_config, "update pub_log set state=%s, finishtime=unix_timestamp(now()) \
                 where pubid=%s ", (2, pubid))
            run_sql(mysql_config, "update cap_crontask set status=%s where tid=%s", (3, tid))
        Ping(self.worker.ip).ping()
        #self.disable()
        task = Task(self.worker.ip)
        return task.set("publog-%s" % publog.pubid, function, callback, lambda *x: None, stdout_callback, stderr_callback,
             timeout=600, timeout_callback=timeout_callabck)


    @property
    def run_function(self,is_manual=False):
        def _run_function(tid=self.tid, mysql_config=self.mysql_config, repo_url=self.repo.repo_url,
                          version=self.version, run_cmd=self.run_cmd,work_dir=self.worker.work_dir):

            def run_command(shell_cmd):
                import sys, datetime, os
                if sys.getdefaultencoding()!="utf-8":
                    reload(sys)
                    sys.setdefaultencoding("utf-8")
                result = os.system(shell_cmd)
                if result == 0:
                    pass
                else:
                    sys.stderr.write("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                    shell_cmd, result))
                    #sys.stderr.flush()
                    raise Exception("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                   shell_cmd, result))

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid
            import os
            import time
            run_sql(mysql_config,'''delete from  cap_runlog  where tid=%s and type='cron' and rid < \
             (select min(rid) from ( select rid  from cap_runlog where \
                  tid=%s and type='cron' order by rid desc limit  100) t)''',(tid,tid))
            rid = run_sql(mysql_config, "insert into cap_runlog(tid,`type`,repo_url,version,addtime,begintime,status,stdout,stderror) \
                             values(%s,'cron',%s,%s,unix_timestamp(now()),unix_timestamp(now()),1,'','')",
                          (tid, repo_url, version))
            time.sleep(0.8)
            run_sql(mysql_config, "update cap_crontask set runlog_rid=%s,run_times=run_times+1 where tid=%s", (rid, tid))
            code_content_dir = os.path.join(work_dir,"cron",str(tid),"code_dir")
            run_command("cd %s &&%s"%(code_content_dir,run_cmd))

        return _run_function

    @property
    def run_stdout_callback(self):
        def _run_stdout_callback(stdout, is_right, tid=self.tid, mysql_config=self.mysql_config):
            def run_query(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid

            if is_right:
                status = 2
            else:
                status = 3
            print "rid"
            rid = run_query(mysql_config, "select runlog_rid from cap_crontask where tid=%s", (tid,))[0][0]
            rid = int(rid)
            print rid
            run_sql(mysql_config, "update cap_runlog  set stdout=%s ,status=%s ,endtime=unix_timestamp(now())\
                                           where rid=%s", (stdout, status, rid))

        return _run_stdout_callback

    @property
    def run_stderr_callback(self):
        def _run_stderr_callback(stderr, is_right, tid=self.tid, mysql_config=self.mysql_config):
            def run_query(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid

            if is_right:
                status = 2
            else:
                status = 3
            print "rid"
            rid = run_query(mysql_config, "select runlog_rid from cap_crontask where tid=%s", (tid,))[0][0]
            rid = int(rid)
            print rid
            run_sql(mysql_config, "update cap_runlog  set stderror=%s ,status=%s ,endtime=unix_timestamp(now())\
                                           where rid=%s", (stderr, status, rid))

        return _run_stderr_callback


    def enable(self):
        cron = Cron(self.worker.ip)
        if self.status == 0 or self.status==2: #待部署   正在部署
            raise Exception("当前任务正在部署,请稍后再操作！")
        if self.status == 3:
            self.pure_init()
            return
        cron.set(self.key, self.rule, self.run_function, lambda *x: None, lambda *x: None,
                 self.run_stdout_callback, self.run_stderr_callback)
        self.status = 1
        self.save()

    def disable(self,delete=False):
        if not delete:
            cron = Cron(self.worker.ip)
            if self.status == 0 or self.status == 2:
                raise Exception("当前任务正在部署,请稍后再操作！")
            if self.status == 3:
                raise Exception("当前任务状态为部署失败，仅可进行删除/修改。")
            if self.worker.is_alive():
                cron.delete("%s" % self.tid)
            self.status = -1
            self.save()
        else:
            if self.worker.is_alive():
                cron = Cron(self.worker.ip)
                cron.delete("%s" % self.tid)
            self.delete()



    def run_once(self):
        cron = Cron(self.worker.ip)
        if self.status != 1:
            raise Exception("当前任务状态为%s,不允许执行此操作！"%self.get_status())
        cron.set(self.key, self.rule, self.run_function, lambda *x: None, lambda *x: None,
                 self.run_stdout_callback, self.run_stderr_callback)
        cron.run_now("%s"%self.tid)




class DeamonTask(models.Model):
    tid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, db_index=True, verbose_name="名称")
    worker_id = models.PositiveIntegerField(default=0, verbose_name="worker id")
    addtime = models.IntegerField(verbose_name="创建时间", default=lambda: int(time.time()))
    uptime = models.IntegerField(verbose_name="修改时间", default=lambda: int(time.time()))
    status = models.IntegerField(default=0, verbose_name="状态")  # -1 禁用      1  启用   0  待部署  2正在部署  3部署失败
    repo_id = models.PositiveIntegerField(default=0)
    version = models.CharField(verbose_name="版本", default='',max_length=50)
    pre_build = models.CharField(max_length=200, default='')
    info = models.CharField(verbose_name="说明", max_length=300)
    owner = models.CharField(verbose_name="所属人", db_index=True, max_length=300)
    run_cmd = models.CharField(verbose_name="参数", max_length=500)  # 运行参数
    run_times = models.PositiveIntegerField(default=0)
    group_id = models.PositiveIntegerField(default=0)
    runlog_rid = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "后台任务"
        verbose_name_plural = "所有后台任务"

    @property
    def worker(self):
        return Worker.objects.get(id=self.worker_id)

    @property
    def group(self):
        return Group.objects.get(id=self.group_id)

    def get_status(self):
        return {-1: "禁用", 1: "启用", 0: "待部署", 2: "正在部署", 3: "部署失败"}[self.status]

    @property
    def repo(self):
        repo_id = self.repo_id
        return Repo.objects.get(id=repo_id)

    @property
    def key(self):
        return str(self.tid)

    @property
    def mysql_config(self):
        return {"host": settings.DATABASES["default"]["HOST"],
                "port": int(settings.DATABASES["default"]["PORT"]),
                'user': settings.DATABASES["default"]["USER"],
                "passwd": settings.DATABASES["default"]["PASSWORD"],
                "db": settings.DATABASES["default"]["NAME"],
                "charset": "utf8"}

    def pure_init(self):
        self.__module__ = "__main__"
        if not self.worker.is_alive():
            raise Exception("该节点已经下线!")
        deamon = Deamon(self.worker.ip)
        if deamon.get(self.key):
            deamon.delete(self.key)
        publog = PubLog(target_id=self.tid, target_type="deamon", state=0)
        publog.save()
        self.status = 0
        self.save()

        def function(pubid=publog.pubid, repo_url=self.repo.repo_url, type=self.repo.type, user=self.repo.user,
                     password=self.repo.password,
                     version=self.version, work_dir=self.worker.work_dir, mysql_config=self.mysql_config,
                     pre_build=self.pre_build, tid=self.tid):
            import os
            import urlparse
            import urllib
            import datetime

            def run_command(shell_cmd):
                import sys, datetime, os
                if sys.getdefaultencoding() != "utf-8":
                    reload(sys)
                    sys.setdefaultencoding("utf-8")
                result = os.system(shell_cmd)
                if result == 0:
                    pass
                else:
                    sys.stderr.write("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                    shell_cmd, result))
                    # sys.stderr.flush()
                    raise Exception("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                   shell_cmd, result))

            def run_sql(mysql_conf, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_conf)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            run_sql(mysql_config, "update cap_deamontask set status=2 where tid=%s and status=0", (tid,))
            run_sql(mysql_config, "update pub_log set state=1  where pubid=%s", (pubid,))
            print "[%s]开始拉取代码：..." % datetime.datetime.now()
            code_dir = os.path.join(work_dir, "task", "%s" % tid)
            run_command("rm -rf %s" % code_dir)
            run_command("mkdir -p %s" % code_dir)
            if type == 1:  # svn
                command = "cd %s && svn checkout  -r %s  %s  code_dir --username %s --password %s \
                                --no-auth-cache --non-interactive" % (
                    code_dir, version, repo_url, user, password)
            else:  # git
                url_object = urlparse.urlparse(repo_url)
                if user or password:
                    command = "cd %s && git clone https://%s:%s@%s%s  code_dir  -b  master    && cd  code_dir && git reset \
                          --hard   %s" % (code_dir, urllib.quote(user), urllib.quote(password),
                                          url_object.netloc, url_object.path, version)
                else:
                    command = "cd %s && git clone %s  code_dir  -b  master    && cd  code_dir && git reset \
                                              --hard   %s" % (code_dir, repo_url, version)

            run_command(command)
            print "[%s]拉取代码完成：Success!" % (datetime.datetime.now())
            print "[%s]开始预处理代码:......" % (datetime.datetime.now())
            if pre_build.strip():
                run_command("cd %s/code_dir &&%s" % (code_dir, pre_build))
            print "[%s]预处理代码完成：Success!" % (datetime.datetime.now())

        def callback(_, pubid=publog.pubid, mysql_config=self.mysql_config, ip=self.worker.ip,
                     run_function=self.run_function, run_stdout_callback=self.run_stdout_callback,
                     run_stderr_callback=self.run_stderr_callback, tid=self.tid):
            def run_sql(mysql_conf, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_conf)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            run_sql(mysql_config, "update cap_deamontask set status=1 where tid=%s and status>=0", (tid,))
            import xmlrpclib, cloudpickle
            server = xmlrpclib.ServerProxy("http://%s:9913" % ip)
            run_function = cloudpickle.dumps(run_function)
            empty_function = cloudpickle.dumps(lambda *x: None)
            run_stdout_callback = cloudpickle.dumps(run_stdout_callback)
            run_stderr_callback = cloudpickle.dumps(run_stderr_callback)
            server.deamon_set("%s" % tid,  xmlrpclib.Binary(run_function),
                            xmlrpclib.Binary(empty_function),
                            xmlrpclib.Binary(empty_function),
                            xmlrpclib.Binary(run_stdout_callback),
                            xmlrpclib.Binary(run_stderr_callback),
                            )

        def stdout_callback(stdout, is_right, mysql_config=self.mysql_config, pubid=publog.pubid, tid=self.tid):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            if is_right:
                state = 4
            else:
                state = 3
            run_sql(mysql_config, "update pub_log set stdout=%s , finishtime=unix_timestamp(now()) \
                     where pubid=%s ", (stdout, pubid,))
            run_sql(mysql_config, "update pub_log set state=%s  where pubid=%s and \
                    state!=2", (state, pubid,))
            if not is_right:
                run_sql(mysql_config, "update cap_deamontask set status=%s where tid=%s", (3, tid))

        def stderr_callback(stdout, is_right, mysql_config=self.mysql_config, pubid=publog.pubid, tid=self.tid):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            if is_right:
                state = 4
            else:
                state = 3
            run_sql(mysql_config, "update pub_log set stderr=%s , finishtime=unix_timestamp(now()) \
                                 where pubid=%s ", (stdout, pubid,))
            run_sql(mysql_config, "update pub_log set state=%s  where pubid=%s and \
                                state!=2", (state, pubid,))
            if not is_right:
                run_sql(mysql_config, "update cap_deamontask set status=%s where tid=%s", (3, tid))

        def timeout_callabck(pubid=publog.pubid, tid=self.tid, mysql_config=self.mysql_config):
            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                cursor.close()
                conn.close()

            run_sql(mysql_config, "update pub_log set state=%s, finishtime=unix_timestamp(now()) \
                     where pubid=%s ", (2, pubid))
            run_sql(mysql_config, "update cap_deamontask set status=%s where tid=%s", (3, tid))

        Ping(self.worker.ip).ping()
        # self.disable()
        task = Task(self.worker.ip)
        return task.set("publog-deamon-%s" % publog.pubid, function, callback, lambda *x: None, stdout_callback,
                        stderr_callback,
                        timeout=600, timeout_callback=timeout_callabck)

    @property
    def run_function(self, is_manual=False):
        def _run_function(tid=self.tid, mysql_config=self.mysql_config, repo_url=self.repo.repo_url,
                          version=self.version, run_cmd=self.run_cmd, work_dir=self.worker.work_dir,ip=self.worker.ip):

            def run_command(shell_cmd):
                import sys, datetime, os
                if sys.getdefaultencoding() != "utf-8":
                    reload(sys)
                    sys.setdefaultencoding("utf-8")
                result = os.system(shell_cmd)
                if result == 0:
                    pass
                else:
                    sys.stderr.write("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                    shell_cmd, result))
                    # sys.stderr.flush()
                    raise Exception("[%s]:Error,命令%s执行返回值是%s,正常情况下shell命令应返回0." % (datetime.datetime.now(),
                                                                                   shell_cmd, result))

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid

            import os
            run_sql(mysql_config, '''delete from  cap_runlog  where tid=%s and type='deamon' and rid < \
                         (select min(rid) from ( select rid  from cap_runlog where \
                              tid=%s and type='deamon' order by rid desc limit  100) t)''', (tid,tid))
            rid = run_sql(mysql_config, "insert into cap_runlog(tid,`type`,repo_url,version,addtime,begintime,status,stdout,stderror) \
                                 values(%s,'deamon',%s,%s,unix_timestamp(now()),unix_timestamp(now()),1,'','')",
                          (tid, repo_url, version))
            import time
            time.sleep(0.8)
            run_sql(mysql_config, "update cap_deamontask set runlog_rid=%s,run_times=run_times+1 where tid=%s",
                    (rid, tid))
            code_content_dir = os.path.join(work_dir, "task", str(tid), "code_dir")
            run_command("cd %s &&%s" % (code_content_dir, run_cmd))

        return _run_function

    @property
    def run_stdout_callback(self):
        def _run_stdout_callback(stdout, is_right, tid=self.tid, mysql_config=self.mysql_config,ip=self.worker.ip):
            def run_query(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid

            if is_right:
                status = 2
            else:
                status = 3
            print "rid"
            rid = run_query(mysql_config, "select runlog_rid from cap_deamontask where tid=%s", (tid,))[0][0]
            rid = int(rid)
            print rid
            run_sql(mysql_config, "update cap_runlog  set stdout=%s ,status=%s ,endtime=unix_timestamp(now())\
                                               where rid=%s", (stdout, status, rid))

        return _run_stdout_callback

    @property
    def run_stderr_callback(self):
        def _run_stderr_callback(stderr, is_right, tid=self.tid, mysql_config=self.mysql_config,ip=self.worker.ip):
            def run_query(mysql_config, sql, args=None):
                import MySQLdb
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

            def run_sql(mysql_config, sql, args=None):
                import MySQLdb
                lastrowid = None
                conn = MySQLdb.connect(**mysql_config)
                cursor = conn.cursor()
                cursor.execute(sql, args)
                if sql.strip().lower().startswith("insert"):
                    lastrowid = cursor.lastrowid
                conn.commit()
                cursor.close()
                conn.close()
                return lastrowid

            if is_right:
                status = 2
            else:
                status = 3
            rid = run_query(mysql_config, "select runlog_rid from cap_deamontask where tid=%s", (tid,))[0][0]
            rid = int(rid)
            run_sql(mysql_config, "update cap_runlog  set stderror=%s ,status=%s ,endtime=unix_timestamp(now())\
                                               where rid=%s", (stderr, status, rid))

        return _run_stderr_callback

    def enable(self):
        deamon = Deamon(self.worker.ip)
        if self.status == 0 or self.status==2: #待部署   正在部署
            raise Exception("当前任务正在部署,请稍后再操作！")
        if self.status == 3:
            self.pure_init()
            return
        deamon.set(self.key,self.run_function, lambda *x: None, lambda *x: None,
                 self.run_stdout_callback, self.run_stderr_callback)
        self.status = 1
        self.save()

    def disable(self,delete=False):
        # deamon = Deamon(self.worker.ip)
        # deamon.delete("%s" % self.tid)
        # self.status = -1
        # self.save()
        if not delete:
            deamon = Deamon(self.worker.ip)
            if self.status == 0 or self.status == 2:
                raise Exception("当前任务正在部署,请稍后再操作！")
            if self.status == 3:
                raise Exception("当前任务状态为部署失败，仅可进行删除/修改。")
            if self.worker.is_alive():
                deamon.delete("%s" % self.tid)
            self.status = -1
            self.save()
        else:
            if self.worker.is_alive():
                deamon = Deamon(self.worker.ip)
                deamon.delete("%s" % self.tid)
            self.delete()


    def run_now(self):
        "立刻重新执行"
        if self.status == 1:
            deamon = Deamon(self.worker.ip)
            deamon.set(self.key,self.run_function, lambda *x: None, lambda *x: None,
                     self.run_stdout_callback, self.run_stderr_callback)
            self.save()
        else:
            raise Exception("该任务状态为%s,不可立刻重启！"%self.get_status())

    def is_running(self):
        if self.status == 1:
            worker = self.worker
            if worker.is_alive():
                deamon = Deamon(self.worker.ip)
                try:
                    return deamon.is_running(self.key)
                except:
                    return False
            else:
                return False
        else:
            return False


class RunLog(models.Model):
    "任务运行日志"
    rid = models.AutoField(primary_key=True)
    tid = models.IntegerField(db_index=True, verbose_name="任务的id")
    type = models.CharField(db_index=True, verbose_name="任务的类型", max_length=30)
    repo_url = models.CharField(verbose_name="代码库svn路径", max_length=100)
    version = models.CharField(verbose_name="版本", max_length=100)
    addtime = models.IntegerField(verbose_name="创建时间", default=0)
    begintime = models.IntegerField(verbose_name="开始运行时间戳", default=0)
    endtime = models.IntegerField(verbose_name="结束时间戳", default=0)
    status = models.IntegerField(verbose_name="状态", default=0)  # 0 待运行  1 正在运行  2 运行正常完成  3  运行异常退出
    stderror = models.TextField(verbose_name="标准错误")
    stdout = models.TextField(verbose_name="标准输出")

    class Meta:
        verbose_name = "运行日志"
        verbose_name_plural = "所有运行日志"

    def get_status(self):
        _config = {0: "待运行", 1: "正在运行", 2: "运行正常完成", 3: "运行异常退出"}
        return _config[self.status]

    def get_type(self):
        _config = {0: "Cron", 1: "Task"}
        return _config[self.type]

# class ServiceManager(models.Model):
#     "服务管理"
#     sid = models.AutoField(primary_key=True)
#     start_py_function = ''
#     stop_py_function = ''
#     status_py_function = ''
#     parent_sids = models.CharField(max_length=100,default='')
#     addtime = models.PositiveIntegerField(default=0)
#     activetime = models.PositiveIntegerField(default=0)
#
#
#
# class ServiceStatusLog(models.Model):
#     "服务状态监控日志"
#
#     pass


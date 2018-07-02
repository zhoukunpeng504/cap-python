#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  os
import  psutil
import argparse


def main():
    parser = argparse.ArgumentParser(description="启动cap-worker服务")
    parser.add_argument("--master",help="master节点的IP. (default 127.0.0.1)",required=False,default="127.0.0.1")
    parser.add_argument("--work_dir",help="工作目录. (default .)",required=False,default=".")
    parser.add_argument("--host",help="所要绑定的IP地址. (default 0.0.0.0)",required=False,default="0.0.0.0")
    info = parser.parse_args()
    init_1 = psutil.Process(pid=1)
    for i in init_1.children(True):
        cmd_line = i.cmdline()
        mask = 0
        for j in cmd_line:
            if "twistd" in j  or ("cap-worker" in j and 'cap-worker-start' not in j):
                mask += 1
        if mask >= 2:
            print cmd_line
            print "worker已经在运行了！无法执行本次启动操作！"
            sys.exit(123)
    result = os.system("cd %s && twistd --pidfile /tmp/cap-worker.pid --logger cap.log.worker_logger.logger cap-worker --master %s --work_dir %s --host %s "%(
        info.work_dir,info.master,info.work_dir,info.host
    ))
    if not result:
        print "启动cap-worker成功"

#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  psutil
import argparse


def main():
    parser = argparse.ArgumentParser(description="停止cap-master服务")
    init_1 = psutil.Process(pid=1)
    for i in init_1.children(True):
        cmd_line = i.cmdline()
        mask = 0
        for j in cmd_line:
            if "twistd" in j  or ("cap-master" in j and 'cap-master-stop' not in j):
                mask += 1
        if mask >=2:
            worker_process = i
            for k in worker_process.children(True):
                k.send_signal(9)
            worker_process.send_signal(9)
            print "成功停止cap-master"
            sys.exit(0)
    else:
        print "cap-master当前尚未在运行"
        sys.exit(123)


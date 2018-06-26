#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  psutil
import argparse


def main():
    parser = argparse.ArgumentParser(description="停止cap-worker服务")
    init_1 = psutil.Process(pid=1)
    for i in init_1.children(True):
        cmd_line = i.cmdline()
        mask = 0
        for j in cmd_line:
            if "twistd" in j  or ("cap-worker" in j and 'cap-worker-stop' not in j):
                mask += 1
        if mask >=2:
            worker_process = i
            for k in worker_process.children(True):
                k.send_signal(9)
            worker_process.send_signal(9)
            print "成功停止cap-worker"
            sys.exit(0)
    else:
        print "cap-worker当前尚未在运行"
        sys.exit(123)

if __name__ == "__main__":
    main()
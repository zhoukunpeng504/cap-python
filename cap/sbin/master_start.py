#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/18.
# ---------------------------------
import sys
import  os
import  psutil
import argparse
from cap.common.valid_mysql import valid

def main():
    parser = argparse.ArgumentParser(description="启动cap-master服务")
    parser.add_argument("--mysql_url",help="mysql的地址(比如：127.0.0.1:3306/db_test)",required=True)
    parser.add_argument("--mysql_user",help="mysql用户. (比如：test)",required=True)
    parser.add_argument("--mysql_password", help="mysql密码. (比如 123456)", required=True)
    parser.add_argument("--host",help="服务绑定的IP地址. (比如：192.168.1.2 ,default： 0.0.0.0)",
                        required=False,default="0.0.0.0")
    info = parser.parse_args()
    init_1 = psutil.Process(pid=1)
    for i in init_1.children(True):
        cmd_line = i.cmdline()
        mask = 0
        for j in cmd_line:
            if "twistd" in j  or ("cap-master" in j and "cap-master-start" not in j):
                mask += 1
        if mask >=2:
            print "master已经在运行了！无法执行本次启动操作！"
            print cmd_line
            sys.exit(123)
    mysql_url = info.mysql_url.strip()
    try:
        a,b = mysql_url.split(":")
        mysql_host = a
        mysql_port,mysql_db =  b.split("/")
        mysql_port = int(mysql_port)
    except:
        print "mysql相关配置错误"
    else:
        mysql_user = info.mysql_user
        mysql_password = info.mysql_password
        result = valid(mysql_host,mysql_port,mysql_db,mysql_user,mysql_password)
        if not result:
            print "mysql相关配置错误"
            sys.exit(123)
        result = os.system("twistd --pidfile /tmp/cap-master.pid --logger cap.log.master_logger.logger cap-master --mysql_url %s --mysql_user %s --mysql_password %s \
             --host %s "%(
            info.mysql_url,info.mysql_user,info.mysql_password,info.host))
        if not result:
            print "启动cap-master成功"

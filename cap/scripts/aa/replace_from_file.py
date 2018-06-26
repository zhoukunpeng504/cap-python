#coding:utf-8
# write  by  zhou
import os
import sys
import datetime
import re
import time
#
if len(sys.argv) != 3:
    raise Exception("参数错误！")
file_path,dir_path = sys.argv[1],sys.argv[2]
if not os.path.exists(file_path):
    raise Exception("路径不存在！"+file_path)
if not os.path.exists(dir_path):
    raise Exception("路径不存在!"+dir_path)
# file_path  = "./scan.log"
# dir_path = "/root/templates/"
print "文件:",file_path
print "正确代码目录：",dir_path
while True:
    input = raw_input("确定开始处理？(输入Y开始处理,输入N退出)")
    input = input.lower()
    if input in ('y','n'):
        if input == "y":
            break
        else:
            sys.exit(0)


print "开始处理...."
file_path = os.path.abspath(file_path)
print file_path
with open(file_path,"r") as f:
    for path in f.readlines():
        path = path.strip()
        _ = path
        while True:
            _ = os.path.abspath(os.path.join(_,".."))
            dir_name = _.strip("/").split("/")[-1]
            if _ == "/":
                break
            if re.match(".+?\w+\.\w+$",dir_name):
                _ = path[len(_)+1:]
                break
        if _ != "/":
            right_file_path = os.path.join(dir_path,_)
            print right_file_path
            try:
                _f = open(right_file_path,"r")
                content = _f.read()
                _f.close()
            except:
                print "%s处理失败！"%path
                with open("replace.log","a+") as log_f:
                    log_f.write("[%s]:%s处理失败！\n"%(datetime.datetime.now(),path))
            else:
                try:
                    with open(path,"w") as _f:
                        _f.write(content)
                except:
                    pass
                print "%s还原成功！"%path




#coding:utf-8
# write  by  zhou
import os
import sys
import datetime
import re
#from os.path import  expanduser
#
if len(sys.argv) != 2:
    raise Exception("参数错误！")
error_path = sys.argv[1]
if not os.path.exists(error_path):
    raise Exception("目录不存在!"+error_path)
print "错误文件目录：",error_path
while True:
    input = raw_input("确定开始处理？(输入Y开始处理,输入N退出)")
    input = input.lower()
    if input in ('y','n'):
        if input == "y":
            break
        else:
            sys.exit(0)


print "开始处理...."
for root,dirs,files in os.walk(error_path):
    for _f in files:
        file_path = os.path.join(root,_f)
        if _f == "index.html.bak.bak":
            print "重命名 %s %s"%(file_path,file_path.replace(".bak.bak",''))
            os.system("mv %s %s"%(file_path,file_path.replace(".bak.bak",'')))
            php_path = os.path.join(root,"index.php")
            if os.path.exists(php_path):
                os.system("rm -r %s"%php_path)
                print "发现index.html.bak.bak同目录的index.php，已删除！"


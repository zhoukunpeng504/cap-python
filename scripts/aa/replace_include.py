#coding:utf-8
# write  by  zhou
import os
import sys
import datetime
import re

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


def content_handle(content):
    new_content = ''
    is_right = True
    for line in content.split("\n"):
        if line.strip().startswith("@include"):
            _ = line.strip().strip(";").replace("@include","").strip(" ").strip('"').strip("\\").split("\\")
            _ = ''.join([str(len(i)) for i in _])[:10]
            if len(_) == 10 and _[0] * len(_) == _:
                is_right = False
                new_content += ''
            else:
                new_content += ("\n"+line)
        else:
            new_content += ("\n"+line)
    return (is_right,new_content)


print "开始处理...."
for root,dirs,files in os.walk(error_path):
    for _f in files:
        file_path = os.path.join(root,_f)
        if _f.endswith(".php"):
            with open(file_path,"r") as f:
                file_content = f.read()
            is_right,real_content = content_handle(file_content)
            if not is_right:
                with open(file_path+"-bak","w") as f:
                    f.write(file_content)
                with open(file_path,"w") as f:
                    f.write(real_content)
                print "成功处理异常php文件：%s" % file_path
print "处理完成!"

#coding:utf-8
# write  by  zhou
import os
import sys
import datetime
import re
#from os.path import  expanduser
#
if len(sys.argv) != 3:
    raise Exception("参数错误！")
right_path,error_content_path = sys.argv[1],sys.argv[2]
if  not os.path.exists(right_path):
    raise Exception("目录不存在！"+right_path)
if not os.path.exists(error_content_path):
    raise Exception("目录不存在!"+error_content_path)
# right_path  = "./wordpress"
# error_path = "/Users/zhou/majinh.com"
print "正确文件目录:",right_path
print "错误文件目录如下："
for _ in os.listdir(error_content_path):
    _ = os.path.join(error_content_path,_)
    if not os.path.isfile(_):
        print _
while True:
    input = raw_input("确定开始处理？(输入Y开始处理,输入N退出)")
    input = input.lower()
    if input in ('y','n'):
        if input == "y":
            break
        else:
            sys.exit(0)

error_regex = r'''<script type="text/javascript">var _0x2515=.+?</script>'''
js_error_regex = r'''var _0x2515=.+?'''
print "开始处理...."
for error_path in os.listdir(error_content_path):
    error_path = os.path.join(error_content_path,error_path)
    if not os.path.isfile(error_path):
        print "开始处理...",error_path
        for root,dirs,files in os.walk(error_path):
            for _f in files:
                file_path = os.path.join(root,_f)
                if _f.endswith(".html") or _f.endswith(".php") or _f.endswith(".bak.bak"):
                    try:
                        file_content = ''
                        with open(file_path,"r") as f:
                            file_content = f.read()
                    except Exception as e :
                        print "文件读取异常：%s ,%s"%(file_path,str(e))
                    else:
                        if re.findall(error_regex,file_content):
                            print "发现异常文件：%s"%file_path
                            real_content = re.sub(error_regex,'',file_content)
                            try:
                                with open(file_path,"w") as f:
                                    f.write(real_content)
                            except Exception as e :
                                print "文件写入异常：%s ,%s" % (file_path, str(e))
                            else:
                                print "成功处理异常文件：%s"%file_path
                elif _f.endswith(".js"):
                    sub_path = file_path.replace(error_path,"").lstrip("/")
                    right_file_path = os.path.join(right_path,sub_path)
                    try:
                        file_content = ''
                        with open(file_path, "r") as f:
                            file_content = f.read()
                    except Exception as e:
                        print "文件读取异常：%s ,%s" % (file_path, str(e))
                    else:
                        if re.findall(js_error_regex, file_content):
                            print "发现异常JS文件：%s" % file_path
                            real_content = ''
                            try:
                                with open(right_file_path, "r") as f:
                                    real_content = f.read()
                            except Exception as e:
                                print "未找到对应的正确JS文件，尝试清空..."
                                try:
                                    with open(file_path, "w") as f:
                                        f.write('')
                                except Exception as e:
                                    print "文件写入异常：%s ,%s" % (file_path, str(e))
                                else:
                                    print "成功清空异常文件：%s" % file_path
                            else:
                                try:
                                    with open(file_path, "w") as f:
                                        f.write(real_content)
                                except Exception as e:
                                    print "文件写入异常：%s ,%s" % (file_path, str(e))
                                else:
                                    print "成功处理异常文件：%s" % file_path
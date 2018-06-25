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
# if  not os.path.exists(right_path):
#     raise Exception("目录不存在！"+right_path)
if not os.path.exists(error_path):
    raise Exception("目录不存在!"+error_path)
# right_path  = "./wordpress"
# error_path = "/Users/zhou/majinh.com"
#print "正确文件目录:",right_path
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
    for line in  content.split("\n"):
        if line.startswith("@include"):
            line = line.strip().strip(";")
            _ =line.replace("@include","").strip(" ").strip('"').strip("\\").split("\\")
            _ = ''.join([str(len(i)) for i in _])[:10]
            if len(_) == 10 and _[0] * len(_) == _:
                is_right = False
                new_content += ''
            else:
                new_content += "\n"
                new_content += line
        else:
            if line.endswith("?><!--EmpireCMS-->"):
                is_right = False
                new_content += ''
            else:
                new_content += ("\n"+line)
    return (is_right,new_content)

error_regex = r'''<script type="text/javascript">var _0x2515=.+?</script>'''
js_error_regex = r'''var _0x2515=.+?'''
print "开始处理...."
for root,dirs,files in os.walk(error_path):
    for _f in files:
        file_path = os.path.join(root,_f)
        if _f.endswith(".html") or _f.endswith(".php") or _f.endswith(".bak.bak"):
            try:
                file_content = ''
                with open(file_path,"r") as f:
                    file_content = f.read()
            except Exception as e :
                pass
                #print "文件读取异常：%s ,%s"%(file_path,str(e))
            else:
                # if re.findall(error_regex,file_content):
                #     print "发现异常文件：%s"%file_path
                #     real_content = re.sub(error_regex,'',file_content)
                #     try:
                #         with open(file_path,"w") as f:
                #             f.write(real_content)
                #     except Exception as e :
                #         #print "文件写入异常：%s ,%s" % (file_path, str(e))
                #         pass
                #     else:
                #         print "成功处理异常文件：%s"%file_path

                if _f.endswith(".php"):
                    with open(file_path,"r") as f:
                        file_content = f.read()
                    is_right,real_content = content_handle(file_content)
                    if not is_right:
                        with open(file_path,"w") as f:
                            f.write(real_content)
                        print "成功处理异常php文件：%s" % file_path

            if _f == "index.html.bak.bak":
                print "重命名 %s %s"%(file_path,file_path.replace(".bak.bak",''))
                os.system("mv %s %s"%(file_path,file_path.replace(".bak.bak",'')))
                php_path = os.path.join(root,"index.php")
                if os.path.exists(php_path):
                    os.system("rm -r %s"%php_path)
                    print "发现index.html.bak.bak同目录的index.php，已删除！"

        # elif _f.endswith(".js"):
        #     sub_path = file_path.replace(error_path,"").lstrip("/")
        #     right_file_path = os.path.join(right_path,sub_path)
        #     try:
        #         file_content = ''
        #         with open(file_path, "r") as f:
        #             file_content = f.read()
        #     except Exception as e:
        #         print "文件读取异常：%s ,%s" % (file_path, str(e))
        #     else:
        #         if re.findall(js_error_regex, file_content):
        #             print "发现异常JS文件：%s" % file_path
        #             real_content = ''
        #             try:
        #                 with open(right_file_path, "r") as f:
        #                     real_content = f.read()
        #             except Exception as e:
        #                 print "未找到对应的正确JS文件，尝试清空..."
        #                 try:
        #                     with open(file_path, "w") as f:
        #                         f.write('')
        #                 except Exception as e:
        #                     print "文件写入异常：%s ,%s" % (file_path, str(e))
        #                 else:
        #                     print "成功清空异常文件：%s" % file_path
        #             else:
        #                 try:
        #                     with open(file_path, "w") as f:
        #                         f.write(real_content)
        #                 except Exception as e:
        #                     print "文件写入异常：%s ,%s" % (file_path, str(e))
        #                 else:
        #                     print "成功处理异常文件：%s" % file_path
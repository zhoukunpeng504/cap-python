#coding:utf-8
# write  by  zhou

from ..decorators import *
from cap.models import *
from django.contrib.admin.models import User



@web_api(True)
def user_list(request):
    '''用户列表
    所需参数：
    无
    返回数据说明：
     id       用户id
     username 用户名
     addtime  用户创建时间
     is_admin 是否是超级用户
    '''
    post_info = request.POST
    total_count = User.objects.all().order_by("-id").count()
    info = User.objects.all().order_by("-id")
    result = []
    for i in info:
        print dir(i.date_joined)
        result.append({"id":i.id,
                       "username":i.username,
                       "addtime":int(i.date_joined.strftime("%s")),
                       "is_admin":i.is_superuser,
                       })
    return {"total_count":total_count,"user_list":result}



@web_api(True)
def user_add(request):
    '''添加用户
    所需参数：
    username       用户名
    password       密码
    password_again 再次输入密码
    '''
    post_info = request.POST
    username = post_info.get("username","")
    password = post_info.get("password","")
    password_again = post_info.get("password_again","")
    if not username:
        raise FieldError("username","用户名不能为空")
    try:
        User.objects.get(username=username)
    except:
        pass
    else:
        raise FieldError("username", '该用户已存在！')

    if not password:
        raise FieldError("password","密码不能为空")
    if len(password) < 6:
        raise FieldError("password","密码长度不能小于6位")
    if password != password_again:
        raise FieldError("password_again","两次输入的密码不一致")
    _p = User(username=username,password='')
    _p.save()
    _p.set_password(password)
    _p.save()
    return True


@web_api(True)
def user_resetpwd(request):
    '''添加用户
    所需参数：
    username       用户名
    password       密码
    password_again 再次输入密码
    '''
    post_info = request.POST
    username = post_info.get("username","")
    password = post_info.get("password","")
    password_again = post_info.get("password_again","")
    user = User.objects.get(username=username)
    if request.user.username != "admin" and  request.user.username!=user.username:
        raise FieldError("username","非admin用户不能修改其他用户的密码！")
    if user.username == "admin":
        raise FieldError("username","禁止修改admin用户的密码")
    if not password:
        raise FieldError("password","密码不能为空")
    if len(password)<6:
        raise FieldError("password","密码长度不能小于6位")
    if password != password_again:
        raise FieldError("password_again","两次输入的密码不一致")
    user.set_password(password)
    user.save()
    return True


@web_api(True)
def user_delete(request):
    '''
    删除用户
    所需参数：
    username
    '''
    post_info = request.POST
    username = post_info.get("username","")
    user = User.objects.get(username=username)
    if request.user.username != "admin":
        raise FieldError("username","非admin用户不能删除用户！")
    if user.username == "admin":
        raise FieldError("username","禁止删除admin用户！")
    user.delete()
    return True




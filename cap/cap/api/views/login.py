#coding:utf-8
# write  by  zhou

from ..decorators import  *
from cap.models import *
from django.contrib.admin.models import User
from django.contrib.auth.views import auth_login,auth_logout
from django.contrib.auth import  authenticate,login,logout


@web_api()
def login(request):
    '''
    用户登录接口
    测试用户： admin  gc895316
    参数说明：
    username
    password
    '''
    post_info = request.POST
    username = post_info.get("username",'')
    password = post_info.get('password','')
    if not username:
        raise FieldError("username","username不能为空")
    if not password:
        raise FieldError("password","password不能为空")
    try:
        user = User.objects.get(username=username)
    except:
        raise FieldError("username","用户不存在")
    else:
        if user.check_password(password):
            request.apisession["uid"] = user.id
            return True
        else:
            raise FieldError("password","密码不正确")


@web_api()
def logout(request):
    '''
    用户退出登录
    参数说明：
    无

    '''
    if request.user:
        #auth_logout(request)
        del request.apisession["uid"]
    return True
#coding:utf-8
# write  by  zhou

from ..decorators import *


@web_api(True)
def get_my_uid(request):
    '''获取当前登录用户的id
    参数：
    无
    '''
    return request.user.id



@web_api(True)
def get_my_info(request):
    '''获取当前登录用户的详细信息
    参数：
    无
    '''
    return {"id":request.user.id,
            "username":request.user.username,
            }


@web_api(True)
def change_my_password(request):
    '''修改我的密码
    参数：
    password_old  老密码
    password       新密码
    password_again  再次输入新密码
    '''
    post_info = request.POST
    password = post_info.get("password","")
    old_password = post_info.get("password_old","")
    password_again = post_info.get("password_again","")
    user = request.user
    if not user.check_password(old_password):
        raise FieldError("password_old","旧密码不正确！")
    if user.username == "admin":
        raise FieldError("username","admin用户的密码禁止修改")
    if not password:
        raise FieldError("password","密码不能为空")
    if len(password)<6:
        raise FieldError("password","密码长度不能小于6位")
    if password != password_again:
        raise FieldError("password_again","两次输入的密码不一致")
    user.set_password(password)
    user.save()
    return True

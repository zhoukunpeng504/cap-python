#coding:utf-8
# write  by  zhou

from ..decorators import *
from cap.models import *


@web_api(True)
def group_all(request):
    '''获取所有分组
    参数：
    无
    '''
    info = Group.objects.all().order_by("-id")
    result = []
    for i in info:
        result.append({"id":i.id,"name":i.name,
                       "addtime":i.addtime})
    return result


@web_api(True)
def group_add(request):
    '''
    添加分组
    参数：
    name  分组名
    '''
    post_info = request.POST
    name = post_info.get("name")
    info = Group.objects.filter(name=name)
    if info.count():
        raise FieldError("name","该分组已经存在！不可重复添加")
    else:
        _ = Group(name=name)
        _.save()
    return True


@web_api(True)
def group_edit(request):
    '''
    修改分组
    参数：
    id
    name
    '''
    post_info = request.POST
    name = post_info.get("name")
    id = post_info.get("id")
    id = int(id)
    if id == Group.objects.get(name="默认").id:
        raise FieldError("id","默认分组不允许修改！")
    try:
        _ = Group.objects.get(id=id)
    except:
        raise FieldError("id","该分组已经被删除！无法修改。")
    else:
        query_set = Group.objects.filter(name=name)
        if query_set.count() > 0 and query_set[0].id != id:
            raise FieldError("name","该分组名已存在！")
        else:
            _.name = name
            _.save()
            return True


@web_api(True)
def group_delete(request):
    '''
    删除分组
    参数：
    id
    '''
    post_info = request.POST
    id = post_info.get("id","")
    id = int(id)
    if id == Group.objects.get(name="默认").id:
        raise FieldError("id","默认分组不允许删除！")
    _ = Group.objects.filter(id=id)
    if not _.count():
        raise FieldError("id","该分组不存在！")
    if CronTask.objects.filter(group_id=id).count() or DeamonTask.objects.filter(group_id=id).count():
        raise FieldError("id","该分组正在被使用，不允许删除！")
    else:
        _.delete()
        return True

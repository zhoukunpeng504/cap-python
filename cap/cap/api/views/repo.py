#coding:utf-8
# write  by  zhou

from ..decorators import *
from cap.models import *



@web_api(True)
def repo_all(request):
    '''
    获取所有代码库
    参数：
    '''
    total_count = Repo.objects.all().count()
    all = Repo.objects.all().order_by("-id")
    result = []
    for i in all:
        result.append({"id":i.id,
                       "addtime":i.addtime,
                       "type":i.type,
                       "repo_url":i.repo_url,
                       "user":i.user,
                       "password":i.password})
    return {"total_count":total_count,"repo_list":result}


@web_api(True)
def repo_add(request):
    '''
    增加代码库
    参数：
    type      类型       ， 必传， int，  1 svn       2 git
    repo_url  代码仓库地址 ，必传，https://开头  或者svn://开头
    user      代码仓库用户， 必传
    password  代码仓库密码 ，必传，
    '''
    post_info = request.POST
    type = post_info.get("type","")
    type = int(type)
    assert type in (1,2)
    repo_url = post_info.get("repo_url","")
    if not repo_url:
        raise FieldError("repo_url","repo_url不能为空")
    user = post_info.get("user","")
    password = post_info.get("password","")
    if user:
        if not password:
            raise FieldError("password","password不能为空！")
    if password:
        if not user:
            raise FieldError('user',"user不能为空！")
    try:
        Repo.objects.get(repo_url=repo_url)
    except:
        repo = Repo(type=int(type),repo_url=repo_url,user=user,password=password)
        repo.save()
        return  repo.id
    else:
        raise FieldError("repo_url","该代码仓库已存在！请勿重复添加！")


@web_api(True)
def repo_edit(request):
    '''
    更新代码库
    参数：
    id        代码库的id    必传,  int
    type      类型       ， 必传， int，  1 svn       2 git
    repo_url  代码仓库地址 ，必传，https://开头  或者svn://开头
    user      代码仓库用户， 必传
    password  代码仓库密码 ，必传，
    '''
    post_info = request.POST
    id = post_info.get("id","")
    id = int(id)
    repo = Repo.objects.get(id=id)
    type = post_info.get("type","")
    type = int(type)
    assert type in (1,2)
    repo_url = post_info.get("repo_url","")
    try:
        _ = Repo.objects.get(repo_url=repo_url)
        assert _.id != id
    except:
        pass
    else:
        raise FieldError("repo_url","repo_url和现有的代码库重复！")
    if not repo_url:
        raise FieldError("repo_url","repo_url不能为空")
    user = post_info.get("user","")
    password = post_info.get("password","")
    if user:
        if not password:
            raise FieldError("password","password不能为空！")
    if password:
        if not user:
            raise FieldError('user',"user不能为空！")
    repo.type = type
    repo.repo_url = repo_url
    repo.user = user
    repo.password = password
    repo.save()
    return  True


@web_api(True)
def repo_delete(request):
    '''
    删除代码库
    参数：
    id        代码库的id    必传,  int
    '''
    post_info = request.POST
    id = post_info.get("id")
    id = int(id)
    try:
        repo = Repo.objects.get(id=id)
    except Repo.DoesNotExist:
        return True
    else:
        if CronTask.objects.filter(repo_id=id).count() or DeamonTask.objects.filter(repo_id=id).count():
            raise FieldError("id","该代码库正在被使用，无法删除！")
        else:
            repo.delete()
            return True


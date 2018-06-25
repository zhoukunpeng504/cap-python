#coding:utf-8
# write  by  zhou

from ..decorators import *
from cap.models import *
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from txscheduling.cron import CronSchedule


@web_api(True)
def cron_all(request):
    '''获取所有的计划任务
    参数：
    worker_id   int, worker的id,【非必选】，
    group_id    int,group 的id，【非必选】
    status      int,状态 ，【非必选】   -1 禁用      1  启用   0  待部署  2正在部署   3部署失败
    owner       string，创建人，【非必选】，
    page   页数，     默认为 1
    num    每页的个数，默认为10
    '''
    post_info = request.POST
    page = post_info.get("page","1")
    num = post_info.get('num',"10")
    worker_id = post_info.get("worker_id","")
    group_id = post_info.get("group_id","")
    status = post_info.get("status","")
    owner = post_info.get("owner","")
    query_params = {}
    if worker_id:
        query_params["worker_id"] = int(worker_id)
    if group_id:
        query_params["group_id"] = int(group_id)
    if status:
        query_params["status"] = int(status)
    if owner:
        query_params["owner"] = owner
    page = int(page)
    num = int(num)
    all_info = CronTask.objects.filter(**query_params).order_by("-tid")
    paginator = Paginator(all_info,num)
    try:
        info = paginator.page(page)
    except EmptyPage:
        page = 1
        info = paginator.page(1)
    result = {"data_list":[],"total_page":paginator.num_pages,"current_page":page,
              "total_count":paginator.count
              }
    for i in info:
        _ = {}
        group = i.group
        worker = i.worker
        load = worker.cpu_mem_load_now()
        _["tid"] = i.tid
        _["name"] = i.name
        _["uptime"] = i.uptime
        _["run_times"] = i.run_times
        _["rule"] = i.rule
        _["status"] = i.get_status()
        _["group"] = {"id":group.id,"name":group.name}
        _["info"] = i.info
        _["owner"] = i.owner
        _["worker"] = {"ip":worker.ip,
                       "is_alive":worker.is_alive(),
                       "load":load,
                       "total_cpu":worker.total_cpu,
                       "total_mem":worker.total_mem,
                       "id":worker.id}
        _["worker_id"] = worker.id
        result["data_list"].append(_)
    return result


@web_api(True)
def cron_one_info(request):
    '''获取单个计划任务的信息
    参数：
    tid   int, 任务的id,【必选】，
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    tid = int(tid)
    try:
        i = CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        raise FieldError("tid","该任务已被删除！")
    else:
        _ = {}
        group = i.group
        worker = i.worker
        load = worker.cpu_mem_load_now()
        _["tid"] = i.tid
        _["name"] = i.name
        _["uptime"] = i.uptime
        _["run_times"] = i.run_times
        _["rule"] = i.rule
        _["status"] = i.get_status()
        _["group"] = {"id":group.id,"name":group.name}
        _["info"] = i.info
        _["owner"] = i.owner
        _["worker"] = {"ip":worker.ip,
                       "is_alive":worker.is_alive(),
                       "load":load,
                       "total_cpu":worker.total_cpu,
                       "total_mem":worker.total_mem,
                       "id":worker.id}
        _["repo_id"] = i.repo_id
        _["version"] = i.version
        _["pre_build"] = i.pre_build
        _["run_cmd"] = i.run_cmd
        _["worker_id"] = i.worker_id
        _["group_id"] = i.group_id
        return _


@web_api(True)
def cron_add(request):
    '''
    创建计划任务
    参数：
    name      名称
    rule      计划任务规则
    repo_id   代码库id
    version   代码库的版本
    pre_build 预构建命令
    info      说明
    run_cmd   运行命令
    worker_id worker的id
    group_id  分组的id
    '''
    post_info = request.POST
    name = post_info.get("name","")
    rule = post_info.get("rule","").strip()
    repo_id = post_info.get("repo_id","")
    version = post_info.get("version","").strip()
    pre_build = post_info.get("pre_build","")
    info = post_info.get("info","")
    run_cmd = post_info.get("run_cmd","").strip()
    worker_id = post_info.get("worker_id")
    group_id = post_info.get("group_id")
    if not name:
        raise FieldError("name","名称不能为空")
    if not rule:
        raise FieldError("rule","时间规则不能为空")
    try:
        CronSchedule(rule)
    except:
        raise FieldError("rule","时间规则不合法！")
    if not repo_id:
        raise FieldError("repo_id","请选择一个代码库")
    repo_id = int(repo_id)
    Repo.objects.get(id=int(repo_id))
    if not version:
        raise FieldError("version","版本不能为空！")
    if not run_cmd:
        raise FieldError("run_cmd","执行命令不能为空！")
    if not worker_id:
        raise FieldError("worker_id","请选择一个worker节点")
    work_id = int(worker_id)
    _worker = Worker.objects.get(id=int(work_id))
    if not group_id:
        raise FieldError("groupid","请选择一个分组")
    if not _worker.is_alive():
        raise FieldError("worker_id","worker节点已经下线！")
    group_id = int(group_id)
    Group.objects.get(id=group_id)
    _ = CronTask(name=name,rule=rule,repo_id=repo_id,version=version,pre_build=pre_build,info=info,
                 owner=request.user.username,run_cmd=run_cmd,worker_id=work_id,group_id=group_id)
    _.save()
    _.pure_init()
    return True


@web_api(True)
def cron_edit(request):
    '''修改计划任务
    参数：
    tid        计划任务的ID
    name       名称
    rule       计划任务规则
    repo_id    代码库id
    version    代码库的版本
    pre_build  预构建命令
    info       说明
    run_cmd    运行命令
    worker_id  worker的id
    group_id   分组的id
    '''
    post_info = request.POST
    tid = post_info.get("tid").strip()
    name = post_info.get("name","").strip()
    rule = post_info.get("rule","").strip()
    repo_id = post_info.get("repo_id","")
    version = post_info.get("version","").strip()
    pre_build = post_info.get("pre_build","")
    info = post_info.get("info","")
    run_cmd = post_info.get("run_cmd","").strip()
    worker_id = post_info.get("worker_id")
    group_id = post_info.get("group_id")
    tid = int(tid)
    cron = CronTask.objects.get(tid=tid)
    if not name:
        raise FieldError("name","名称不能为空")
    if not rule:
        raise FieldError("rule","时间规则不能为空")
    try:
        CronSchedule(rule)
    except:
        raise FieldError("rule","时间规则不合法！")
    if not repo_id:
        raise FieldError("repo_id","请选择一个代码库")
    repo_id = int(repo_id)
    Repo.objects.get(id=int(repo_id))
    if not version:
        raise FieldError("version","版本不能为空！")
    if not run_cmd:
        raise FieldError("run_cmd","执行命令不能为空！")
    if not worker_id:
        raise FieldError("work_id","请选择一个worker节点")
    work_id = int(worker_id)
    _worker =Worker.objects.get(id=int(work_id))
    if work_id != cron.worker_id:
        raise FieldError("work_id","不允许修改所在的worker节点")
    if not group_id:
        raise FieldError("groupid","请选择一个分组")
    if not _worker.is_alive():
        raise FieldError("worker_id","worker节点已经下线！")
    group_id = int(group_id)
    Group.objects.get(id=group_id)
    if repo_id != cron.repo_id or version != cron.version or pre_build != cron.pre_build:
        cron.name = name
        cron.rule = rule
        cron.repo_id = repo_id
        cron.uptime = int(time.time())
        cron.version = version
        cron.pre_build = pre_build
        cron.info = info
        cron.run_cmd = run_cmd
        cron.group_id = group_id
        cron.save()
        cron.pure_init()
        return True
    else:
        cron.name = name
        cron.rule = rule
        cron.repo_id = repo_id
        cron.uptime = int(time.time())
        cron.version = version
        cron.pre_build = pre_build
        cron.info = info
        cron.run_cmd = run_cmd
        cron.group_id = group_id
        cron.enable()
        return True


@web_api(True)
def cron_delete(request):
    '''删除计划任务
    参数：
    tid    任务的id

    '''
    post_info = request.POST
    tid = post_info.get("tid","")
    tid = int(tid)
    try:
        _ =CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        #raise FieldError("tid","该任务已不存在！")
        return True
    else:
        _.disable(True)
        return True



@web_api(True)
def cron_disable(request):
    '''禁用计划任务
    参数：
    tid   任务的id
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    tid = int(tid)
    try:
        _ = CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        raise FieldError("tid","该任务已不存在！")
    else:
        if _.worker.is_alive():
            try:
                _.disable()
            except Exception as e:
                raise FieldError("tid", str(e))
        else:
            if _.get_status() != "启用":
                raise FieldError("tid","该任务的状态为%s，不可禁用！"%_.get_status())
        _.status = -1
        _.save()
        #_.delete()
        return True



@web_api(True)
def cron_enable(request):
    '''启用计划任务
    参数：
    tid  任务的id
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    tid = int(tid)
    try:
        _ = CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        raise FieldError("tid", "该任务已不存在！")
    else:
        if not _.worker.is_alive():
            raise FieldError("tid","该任务所在节点已离线！无法启用")
        else:
            if _.get_status() != "禁用":
                raise FieldError("tid","该任务的状态为%s，不可启用！"%_.get_status())
            _.enable()
        return True



@web_api(True)
def cron_publog(request):
    '''计划任务的代码拉取日志
    参数：
    tid  任务的id
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    try:
        _ = CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        raise FieldError("tid","该任务不存在")
    else:
        info = PubLog.objects.filter(target_id=tid,target_type="cron").order_by("-pubid")[:10]
        result = []
        for i in info:
            result.append({"pubid":i.pubid,
                           "addtime":i.addtime,
                           "finishtime":i.finishtime,
                           "stdout":i.stdout,
                           "stderr":i.stderr,
                           "state":i.get_state()})
        #result.reverse()
        return result



@web_api(True)
def cron_runlog(request):
    '''计划任务的运行日志
    参数：
    tid 任务的id
    page   页数，     默认为 1
    num    每页的个数，默认为10
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    page = post_info.get("page","1")
    num = post_info.get("num","10")
    page = int(page)
    num = int(num)
    all_info = RunLog.objects.filter(tid=tid,type="cron").order_by("-rid")
    paginator = Paginator(all_info,num)
    try:
        info = paginator.page(page)
    except EmptyPage:
        page = 1
        info = paginator.page(1)
    result = {"data_list":[],"total_page":paginator.num_pages,"current_page":page,
              # "total_num":paginator.count
              }
    for i in info:
        item = {}
        item["repo_url"] = i.repo_url
        item["version"] = i.version
        item["begintime"] = i.begintime
        item["endtime"] = i.endtime
        item["status"] = i.get_status()
        item["stdout"] = i.stdout
        item["stderror"] = i.stderror
        result["data_list"].append(item)
    return result



@web_api(True)
def cron_run_once(request):
    '''执行一次计划任务
    参数：
    tid    任务的id
    '''
    post_info = request.POST
    tid = post_info.get("tid")
    tid = int(tid)
    try:
        _ = CronTask.objects.get(tid=tid)
    except CronTask.DoesNotExist:
        raise FieldError("tid", "该任务已不存在！")
    else:
        if not _.worker.is_alive():
            raise FieldError("tid","该任务所在节点已离线！无法启用")
        else:
            if _.get_status() != "启用":
                raise FieldError("tid","该任务的状态为%s，不可执行！"%_.get_status())
            else:
                _.run_once()
        return True

#coding:utf-8
# write  by  zhou
from ..decorators import *
from cap.models import *
from django.core.paginator import Paginator,EmptyPage,InvalidPage


@web_api(True)
def worker_all(request):
    '''获取所有的worker (此部分不会太多，不用考虑分页)
    参数：
    无
    返回值说明：
    id          worker的ID
    ip          worker的IP
    addtime     worker的加入时间
    is_alive    worker当前是否存活
    last_connect_time  worker上次活跃时间
    total_cpu          worker cpu个数
    total_mem          worker 内存大小(MB)
    '''
    all_info = Worker.objects.all().order_by("-id")
    result = []
    for i in all_info:
        result.append({"id":i.id,
                       "ip":i.ip,
                       "addtime":i.addtime,
                       "is_alive":i.is_alive(),
                       "last_connect_time":i.heartbeat,
                       "total_cpu":i.total_cpu,
                       "total_mem":i.total_mem})
    return result


@web_api(True)
def worker_info(request):
    '''获取单个worker的信息
    参数：
    id    worker的id
    返回值说明：
    id          worker的ID
    ip          worker的IP
    addtime     worker的加入时间
    is_alive    worker当前是否存活
    last_connect_time  worker上次活跃时间
    total_cpu          worker cpu个数
    total_mem          worker内存大小(MB)
    '''
    post_info = request.POST
    id = post_info.get("id")
    id = int(id)
    worker = Worker.objects.get(id=id)
    return {"id":worker.id,
            "ip":worker.ip,
            "addtime":worker.addtime,
            "is_alive":worker.is_alive(),
            "last_connect_time":worker.heartbeat,
            "total_cpu":worker.total_cpu,
            "total_mem":worker.total_mem}


@web_api(True)
def worker_cpu_mem_log(request):
    '''获取单个worker的cpu内存负载信息
    参数：
    id   worker的id
    
    '''
    post_info = request.POST
    id = post_info.get("id")
    id = int(id)
    worker = Worker.objects.get(id=id)
    info = WorkerCpuMemLog.objects.filter(work_id=worker.id).order_by("-id")[:200]
    result = []
    for i in info:
        result.append({"time":i.addtime,
                       "cpu_percent":i.cpu_percent,
                       "mem_percent":i.mem_percent})
    result.reverse()
    return result
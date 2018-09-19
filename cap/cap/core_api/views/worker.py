#coding:utf-8
# write  by  zhou
from django.http import  HttpResponse
import json
from cap.models import  *
from django.conf import  settings

buff = {}

def worker_heartbeat(request):
    get_info = request.GET
    post_info = request.POST
    ip = request.GET.get("ip","") or request.META["REMOTE_ADDR"]
    work_dir = get_info.get("work_dir","")
    num = get_info.get("num","")
    num = int(num)
    worker = Worker.worker_heartbeat(ip,work_dir)
    if num == 1 or not buff.has_key(ip):
        buff[ip] = ip
        worker.pure_init()
        all_cron_task = CronTask.objects.filter(worker_id=worker.id)
        for i in all_cron_task:
            if i.status == 1:
                i.enable()
        all_deamon_task = DeamonTask.objects.filter(worker_id=worker.id)
        for i in all_deamon_task:
            if i.status == 1:
                i.enable()
        if ip == settings.HOST:
            all_repo = Repo.objects.all()
            for i in all_repo:
                i.pure_init()
    else:
        pass
    return HttpResponse("success")







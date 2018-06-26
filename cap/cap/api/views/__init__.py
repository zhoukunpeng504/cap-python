# coding:utf-8
__author__ = 'zhou'
# --------------------------------
# Created by zhou  on 2017/02/20.
# ---------------------------------
from itertools import groupby
from collections import OrderedDict
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import os
from django.http import  HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import sys
from ..utils.aes import *
import random
import time
from ..utils.md5 import *

JsonResponse = lambda x: HttpResponse(json.dumps(x), mimetype="application/javascript")
_modules = os.listdir(os.path.dirname(__file__))
__all__ = [i.replace(".py", "") for i in _modules if i.endswith(".py") and (not i.startswith("__"))]

__all__ += ["api_gateway", "api_document", "meta_test","get_session_key"]


def get_session_key(request):
    key = md5(str(random.random()) + str(time.time()))
    key = aes_encrypt("1" * 16, "bxmppi" + key[16:])
    result = JsonResponse({"errorCode": 0, "data": key, "message": "success", "formError": {}})
    if request.META.get("HTTP_ORIGIN",""):
        result["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN","")
    return result


def meta_test(request):
    data = dict(
        [(i, j) for i, j in request.META.items() if isinstance(i, (str, unicode)) and isinstance(j, (str, unicode))])
    return JsonResponse(data)


@csrf_exempt
def api_gateway(request):
    method = request.GET.get("method", "")
    version = request.GET.get("version", "")
    _ = sys.api_config.get(method)
    if _:
        function = _.get(version) or _.get("")
        if function:
            return function(request)
    return JsonResponse({"errorCode": 404, "data": None, "message": "can not find the method!", "formError": {}})


def api_document(request):
    if hasattr(sys, "api_config"):
        info = sys.api_config.items()
    else:
        info = []
    info.sort(key=lambda x: x[0])
    result = OrderedDict()
    for module_name, _iter in groupby(info, key=lambda x: ".".join(x[0].split(".")[:-1])):
        result[module_name] = []
        for j in _iter:
            ver_list = []
            for k, l in sorted(j[1].items(), key=lambda x: x[0]):
                ver_list.append([k, l.__doc__ or ''])
            result[module_name].append((j[0], ver_list))
    result = result.items()
    return render_to_response("api_document.html", locals(), context_instance=RequestContext(request))


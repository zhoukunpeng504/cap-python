# coding:utf-8


from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import traceback
from .utils.aes import *
from django.utils.importlib import import_module
from django.conf import settings
from .utils.md5 import md5
from django.contrib.admin.models import User

JsonResponse = lambda x: HttpResponse(json.dumps(x, indent=True), mimetype="application/javascript")




class FieldError(Exception):
    def __init__(self, field_name, message):
        Exception.__init__(self)
        self.message = message
        self.field_name = field_name

    def __str__(self):
        return str("$fielderror" + json.dumps({"field_name": self.field_name, "message": self.message}))

    def __unicode__(self):
        return unicode("$fielderror" + json.dumps({"field_name": self.field_name, "message": self.message}))


class ReturnValue(Exception):
    def __init__(self, data, message=""):
        self.data = data
        self.message = message


def web_api(login_required=False):
    version = ''
    versions = ['']
    def _web_api(views):
        @csrf_exempt
        def _(request, *args, **kwargs):

            session_info = request.META.get("HTTP_SESSION", "") or request.GET.get("session","") or \
                request.GET.get("Sesion","") or request.GET.get("SESSION","")
            try:
                assert session_info
                assert aes_decrypt('1' * 16, session_info).startswith("bxmpp")
            except:
                _result = (
                    {"errorCode": 403, "message": "you have no permission to this api", "formError": {}, "data": None})
            else:
                from session_engine import db as engine
                request.apisession = engine.SessionStore(md5(session_info))
                try:
                    value = request.apisession.get("uid")
                    uid = int(value)
                    user = User.objects.get(id=uid)
                    request.myuser = user
                    request.user = user
                except:
                    request.myuser = None
                    request.user = None

                if login_required and request.myuser == None:
                    _result = (
                        {"errorCode": 403, "message": "you have no permission to this api", "formError": {},
                         "data": None})
                else:
                    try:
                        try:
                            result = views(request, *args, **kwargs)
                        except AssertionError as _re:
                            if str(_re).startswith("$fielderror"):
                                _re_info = str(_re).strip("$fielderror")
                                _re_info = json.loads(_re_info)
                                raise FieldError(_re_info["field_name"], _re_info["message"])
                            else:
                                raise Exception("AssertError")
                    except  FieldError as e:
                        _result = ({"errorCode": 0, "message": e.message, "formError":
                            {"name": e.field_name, "message": e.message}, "data": None})
                    except Exception as e:
                        e_traceback =  traceback.format_exc()
                        print e_traceback
                        _result = ({"errorCode": 500, "message": str(e), "formError":
                            {}, "data": None,"traceback":e_traceback})
                    else:
                        message = ""
                        if isinstance(result, ReturnValue):
                            message = result.message
                            result = result.data
                        _result = ({"errorCode": 0, "message": message, "formError": {}, "data": result})
                    try:
                        modified = request.apisession.modified
                        empty = request.apisession.is_empty()
                    except AttributeError:
                        pass
                    else:
                        print modified, empty
                        if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                            print "save....."
                            request.apisession.save()

            result =  JsonResponse(_result)
            if request.META.has_key("HTTP_ORIGIN"):
                result["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN")
            print result
            return result
        _.__doc__ = views.__doc__
        if not getattr(sys, "api_config", None):
            sys.api_config = {}
        if not sys.api_config.get(views.__module__ + "." + views.__name__):
            sys.api_config[views.__module__ + "." + views.__name__] = {}
        if not version:
            sys.api_config[views.__module__ + "." + views.__name__][''] = _
        else:
            for ver in versions:
                sys.api_config[views.__module__ + "." + views.__name__][ver] = _
        return _

    return _web_api


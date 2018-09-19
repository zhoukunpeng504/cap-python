#coding:utf-8
# write  by  zhou

#coding:utf-8
# write  by  zhou

import base64
import json
import  cloudpickle
import  traceback
import sys
import time
# from django.conf import  settings
# settings.configure()
reload(sys)
sys.setdefaultencoding("utf-8")
time.sleep(0.1)
_=raw_input()
_=_.strip()
data=cloudpickle.loads(base64.b64decode(_))
fun,callback,errback=data["fun"],data["callback"],data["errback"]
args,kwargs=data["args"],data["kwargs"]

return_code=0
try:
    result=fun(*args,**kwargs)
except Exception as e :
    error_msg= "fun exception:"+str(e)
    sys.stderr.write(error_msg)
    traceback.print_exc()
    return_code=1
    try:
        errback(str(e))
    except Exception as e :
        error_msg= "errback exception:"+str(e)
        sys.stderr.write(error_msg)
        traceback.print_exc()
        pass
else:
    try:
        callback(result)
    except Exception as e :
        error_msg= "callback exception:"+str(e)
        sys.stderr.write(error_msg)
        traceback.print_exc()
        return_code=1
sys.exit(return_code)




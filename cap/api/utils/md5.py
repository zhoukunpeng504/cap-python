#coding:utf-8
# write  by  zhou
import hashlib


def md5(str):
    return  hashlib.md5(str).hexdigest()
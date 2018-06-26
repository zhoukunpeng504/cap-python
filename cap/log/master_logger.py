# coding:utf-8
# write  by  zhou

from twisted.python.log import *
from twisted.python.logfile import DailyLogFile
from twisted.python import logfile

f = logfile.LogFile("cap-master.log", '/tmp',
                    rotateLength=10000000,
                    maxRotatedFiles=10)
flobserver = FileLogObserver(f)
def logger():
    observer = flobserver.emit
    return observer
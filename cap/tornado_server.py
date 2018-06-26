import os
import sys
from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_HERE)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cap.settings'

def main(master_port,mysql_host,mysql_port,mysql_db,mysql_user,mysql_password):
    os.mysql_host = mysql_host
    os.mysql_port = mysql_port
    os.mysql_db = mysql_db
    os.mysql_user = mysql_user
    os.mysql_password = mysql_password
    wsgi_app = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application(
            [
                ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            ]
            )
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(master_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main(8080,"192.168.14.90",3306,"cap_test","spider","123456")

"""
Main launching point of the vFense Server
"""
import os
import base64
import uuid
import logging
import logging.config

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

from vFense.core.scheduler.manager import start_scheduler
from vFense.utils.common import import_modules_by_regex, get_api_uris
from vFense._constants import (
    VFENSE_LOGGING_CONFIG, VFENSE_TEMPLATE_PATH, VFENSE_SSL_PATH,
    VFENSE_APP_PATH, VFENSE_WWW_PATH
)


define("port", default=9000, help="run on port", type=int)
define("debug", default=True, help="enable debugging features", type=bool)


class HeaderModule(tornado.web.UIModule):
    def render(self):
        return self.render_string(
            os.path.join(VFENSE_TEMPLATE_PATH, "header.html")
        )


class Application(tornado.web.Application):
    def __init__(self, debug):
        dynamic_handlers = get_api_uris()
        whitelist = [

            ##### File system access whitelist
            (r"/css/(.*?)", tornado.web.StaticFileHandler,
                {"path": os.path.join(VFENSE_WWW_PATH, "css")}),
            (r"/font/(.*?)", tornado.web.StaticFileHandler,
                {"path": os.path.join(VFENSE_WWW_PATH, "font")}),
            (r"/img/(.*?)", tornado.web.StaticFileHandler,
                {"path": os.path.join(VFENSE_WWW_PATH, "img")}),
            (r"/js/(.*?)", tornado.web.StaticFileHandler,
                {"path": os.path.join(VFENSE_WWW_PATH, "js")}),
            (r"/packages/*/(.*?)", tornado.web.StaticFileHandler,
                {"path": VFENSE_APP_PATH})
        ]

        handlers = dynamic_handlers + whitelist

        settings = {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes +
                                              uuid.uuid4().bytes),
            "login_url": "/login",
        }
        self.scheduler = start_scheduler()
        tornado.web.Application.__init__(self, handlers,
                                         template_path=VFENSE_TEMPLATE_PATH,
                                         debug=debug, **settings)

    def log_request(self, handler):
        logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
        log = logging.getLogger('rvweb')
        log_method = log.debug
        if handler.get_status() <= 299:
            log_method = log.info
        elif handler.get_status() <= 399 and \
                handler.get_status() >= 300:
            log_method = log.warn
        elif handler.get_status() <= 499 and \
                handler.get_status() >= 400:
            log_method = log.error
        elif handler.get_status() <= 599 and \
                handler.get_status() >= 500:
            log_method = log.error
        request_time = 1000.0 * handler.request.request_time()
        real_ip = handler.request.headers.get('X-Real-Ip', None)
        #remote_ip = handler.request.remote_ip
        #uri = handler.request.remote_ip
        forwarded_ip = handler.request.headers.get('X-Forwarded-For', None)
        user_agent = handler.request.headers.get('User-Agent')
        log_message = '%d %s %s, %.2fms' % (handler.get_status(), handler._request_summary(), user_agent, request_time)
        if real_ip:
            log_message = '%d %s %s %s %s, %.2fms' % (handler.get_status(), handler._request_summary(), real_ip, forwarded_ip, user_agent, request_time)
        log_method(log_message)

if __name__ == '__main__':
    import_modules_by_regex('_db_init')
    tornado.options.parse_command_line()
    https_server = tornado.httpserver.HTTPServer(
        Application(options.debug),
        ssl_options={
            "certfile": os.path.join(VFENSE_SSL_PATH, "server.crt"),
            "keyfile": os.path.join(VFENSE_SSL_PATH, "server.key")
        }
    )
    https_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


import tornado.httpserver
import tornado.web

import simplejson as json

from vFense.server.handlers import BaseHandler
import logging
import logging.config

from vFense.plugins.patching import *
from vFense.errorz.error_messages import GenericResults, PackageResults

from vFense.plugins.patching.rv_db_calls import get_all_file_data
from vFense.server.hierarchy.manager import get_current_customer_name
from vFense.server.hierarchy.decorators import authenticated_request, permission_check
from vFense.server.hierarchy.decorators import convert_json_to_arguments
from vFense.server.hierarchy.permissions import Permission

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class FileInfoHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri = self.request.uri
        method = self.request.method
        try:
            results = get_all_file_data()
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('', 'get all file data', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


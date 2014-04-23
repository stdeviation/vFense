import simplejson as json
import logging
import logging.config

from vFense.core.api.base import BaseHandler
from vFense.plugins.patching import *
from vFense.errorz.error_messages import GenericResults

from vFense.plugins.patching.rv_db_calls import get_all_file_data
from vFense.core.decorators import authenticated_request

from vFense.core.user import UserKeys
from vFense.core.user.users import get_user_property

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class FileInfoHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
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


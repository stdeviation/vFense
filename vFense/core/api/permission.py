import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import authenticated_request

from vFense.core.permissions._constants import Permissions
from vFense.core.results import Results, ApiResultKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveValidPermissionsHandler(BaseHandler):

    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        count = 0
        permissions = []
        try:
            permissions = Permissions.get_valid_permissions()
            count = len(permissions)
            data = {
                ApiResultKeys.DATA: permissions,
                ApiResultKeys.COUNT: count
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).information_retrieved(**data)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Retrieving permissions broke: {0}'.format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

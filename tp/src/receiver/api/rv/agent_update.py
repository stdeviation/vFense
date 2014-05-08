import logging

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import agent_authenticated_request, \
    convert_json_to_arguments
from vFense.core.user.users import get_user_property
from vFense.core.user import UserKeys
from vFense.receiver.rvhandler import RvHandOff

from vFense.operations._constants import AgentOperations

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvlistener')


class AgentUpdateHandler(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self, agent_id):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )

        uri = self.request.uri
        method = self.request.method

        try:
            operation_id = self.arguments.get('operation_id', None)
            error = self.arguments.get('error', None)
            success = self.arguments.get('success', 'true')
            app_data = self.arguments.get('data')
            status_code = self.arguments.get('status_code', None)

            #RvHandOff(
            #   username, customer_name, uri, method, agent_id,
            #   app_data, oper_type=AgentOperations.AVAILABLE_AGENT_UPDATE
            #)
            hand_off = RvHandOff()
            hand_off.available_agent_update_operation(agent_id, app_data)

        except Exception as e:
            logger.exception(e)


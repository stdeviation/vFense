import simplejson as json

from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import (
    ApiArguments, AgentApiArguments, ApiValues, TagApiArguments
)
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations import AgentOperation
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.core.agent._db_model import AgentKeys
from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.agent.search.search import RetrieveAgents
from vFense.core.agent.manager import AgentManager
from vFense.core.tag import Tag
from vFense.core.tag.manager import TagManager
from vFense.core.view.manager import ViewManager
from vFense.core.view._db import token_exist_in_current
from vFense.core.queue.uris import get_result_uris
from vFense.core.results import ExternalApiResults, ApiResults

from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)
from vFense.core.agent.operations.store_agent_operations import (
    StoreAgentOperations
)
from vFense.core.agent.agents import (
    get_supported_os_codes, get_supported_os_strings, get_environments
)

from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)
from vFense.core.agent.status_codes import AgentCodes, AgentFailureCodes
from vFense.core.view.status_codes import ViewCodes


class AgentStats(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id, stat):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        if stat == 'cpu':
            results = self.get_cpu(agent_id)
        elif stat == 'memory':
            results = self.get_memory(agent_id)
        else:
            results = self.get_filesystems(agent_id)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'stats')

    @results_message
    @check_permissions(Permissions.READ)
    def get_cpu(self, agent_id):
        results = get_result_uris(agent_id)
        results.count = len(results.data)
        return results




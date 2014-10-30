import simplejson as json
import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import (
    ApiArguments, AgentOperationsApiArguments
)
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.operations._db_model import (
    AgentOperationKey
)
from vFense.core.operations.agent_operations import get_agent_operation
from vFense.core.operations.search.agent_search import AgentOperationRetriever
from vFense.core.decorators import (
    authenticated_request, results_message, catch_it
)
from vFense.core.results import (
    ExternalApiResults
)
from vFense.core.user.manager import UserManager
from vFense.core.user import UserKeys
from vFense.core.status_codes import GenericCodes

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class GetTransactionsHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
        sort_by = (
            self.get_argument(
                ApiArguments.SORT_BY, AgentOperationKey.CreatedTime
            )
        )
        operation = (
            self.get_argument(AgentOperationsApiArguments.OPERATION, None)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        search = (
            AgentOperationRetriever(active_view, count, offset, sort, sort_by)
        )

        if operation:
            results = self.get_operations_by_type(search, operation)

        else:
            results = self.get_all_operations(search)

        self.set_status(results.http_status_code)
        self.modified_output(results.to_dict_non_null(), output, 'operations')

    @results_message
    def get_operations_by_type(self, search, operation):
        results = search.by_operation(operation)
        return results

    @results_message
    def get_all_operations(self, search):
        results = search.all()
        return results

class AgentOperationsHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
        sort_by = (
            self.get_argument(
                ApiArguments.SORT_BY, AgentOperationKey.CreatedTime
            )
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        search = (
            AgentOperationRetriever(active_view, count, offset, sort, sort_by)
        )

        results = self.get_agent_operations(search, agent_id)

        self.set_status(results.http_status_code)
        self.modified_output(results.to_dict_non_null(), output, 'operations')

    @results_message
    def get_agent_operations(self, search, agent_id):
        results = search.by_agentid(agent_id)
        return results


class TagOperationsHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self, tag_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
        sort_by = (
            self.get_argument(
                ApiArguments.SORT_BY, AgentOperationKey.CreatedTime
            )
        )

        search = (
            AgentOperationRetriever(active_view, count, offset, sort, sort_by)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_tag_operations(search, tag_id)

        self.set_status(results.http_status_code)
        self.modified_output(results.to_dict_non_null(), output, 'operations')

    @results_message
    def get_tag_operations(self, search, tag_id):
        results = search.by_tagid(tag_id)
        return results

class OperationHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self, operation_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
        sort_by = (
            self.get_argument(
                ApiArguments.SORT_BY, AgentOperationKey.CreatedTime
            )
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        search = (
            AgentOperationRetriever(active_view, count, offset, sort, sort_by)
        )

        operation_data = get_agent_operation(operation_id)
        if operation_data:
            if re.search('install', operation_data[AgentOperationKey.Operation]):
                results = self.get_install_operation_by_id(search, operation_id)
            else:
                results = self.get_operation_by_id(search, operation_id)

        self.set_status(results.http_status_code)
        self.modified_output(results.to_dict_non_null(), output, 'operations')

    @results_message
    def get_operation_by_id(self, search, operation_id):
        results = search.by_id(operation_id)
        return results

    @results_message
    def get_install_operation_by_id(self, search, operation_id):
        results = search.install_operation_by_id(operation_id)
        return results

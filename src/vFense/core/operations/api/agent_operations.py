import simplejson as json
import re
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import ApiArguments
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.operations._db_model import *
from vFense.core.operations.agent_operations import get_agent_operation
from vFense.core.operations.search.agent_search import AgentOperationRetriever
from vFense.core.decorators import authenticated_request, results_message
from vFense.result.error_messages import GenericResults
from vFense.core.user.manager import UserManager
from vFense.core.user import UserKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class GetTransactionsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = (
                int(
                    self.get_argument(ApiArguments.COUNT,
                        DefaultQueryValues.COUNT
                    )
                )
            )
            offset = (
                int(
                    self.get_argument(
                        ApiArguments.OFFSET,
                        DefaultQueryValues.OFFSET
                    )
                )
            )
            sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
            sort_by = (
                self.get_argument(
                    ApiArguments.SORT_BY,
                    AgentOperationKey.CreatedTime
                )
            )
            operation = self.get_argument(ApiArguments.OPERATION, None)

            search = (
                AgentOperationRetriever(
                    view_name, count, offset, sort, sort_by,
                )
            )

            if operation:
                results = self.get_operations_by_type(search, operation)

            else:
                results = self.get_all_operations(search)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('operation', 'search by oper type', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_operations_by_type(self, search, operation):
        results = search.get_all_by_operation(operation)
        return results

    @results_message
    def get_all_operations(self, search):
        results = search.get_all()
        return results

class AgentOperationsHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = (
                int(
                    self.get_argument(ApiArguments.COUNT,
                        DefaultQueryValues.COUNT
                    )
                )
            )
            offset = (
                int(
                    self.get_argument(
                        ApiArguments.OFFSET,
                        DefaultQueryValues.OFFSET
                    )
                )
            )
            sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
            sort_by = (
                self.get_argument(
                    ApiArguments.SORT_BY,
                    AgentOperationKey.CreatedTime
                )
            )

            search = (
                AgentOperationRetriever(
                    view_name, count, offset, sort, sort_by,
                )
            )

            results = self.get_agent_operations(search, agent_id)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('operation', 'search by oper type', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_agent_operations(self, search, agent_id):
        results = search.get_all_by_agentid(agent_id)
        return results


class TagOperationsHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = (
                int(
                    self.get_argument(ApiArguments.COUNT,
                        DefaultQueryValues.COUNT
                    )
                )
            )
            offset = (
                int(
                    self.get_argument(
                        ApiArguments.OFFSET,
                        DefaultQueryValues.OFFSET
                    )
                )
            )
            sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
            sort_by = (
                self.get_argument(
                    ApiArguments.SORT_BY,
                    AgentOperationKey.CreatedTime
                )
            )

            search = (
                AgentOperationRetriever(
                    view_name, count, offset, sort, sort_by,
                )
            )

            results = self.get_tag_operations(search, tag_id)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('operation', 'search by oper type', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_tag_operations(self, search, tag_id):
        results = search.get_all_by_tagid(tag_id)
        return results

class OperationHandler(BaseHandler):
    @authenticated_request
    def get(self, operation_id):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = (
                int(
                    self.get_argument(ApiArguments.COUNT,
                        DefaultQueryValues.COUNT
                    )
                )
            )
            offset = (
                int(
                    self.get_argument(
                        ApiArguments.OFFSET,
                        DefaultQueryValues.OFFSET
                    )
                )
            )
            sort = self.get_argument(ApiArguments.SORT, SortValues.DESC)
            sort_by = (
                self.get_argument(
                    ApiArguments.SORT_BY,
                    AgentOperationKey.CreatedTime
                )
            )

            search = (
                AgentOperationRetriever(
                    view_name, count, offset, sort, sort_by,
                )
            )

            operation_data = get_agent_operation(operation_id)
            if operation_data:
                if re.search('install', operation_data[AgentOperationKey.Operation]):
                    results = self.get_install_operation_by_id(search, operation_id)
                else:
                    results = self.get_operation_by_id(search, operation_id)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('operation', 'search by oper type', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_operation_by_id(self, search, operation_id):
        results = search.get_operation_by_id(operation_id)
        return results

    @results_message
    def get_install_operation_by_id(self, search, operation_id):
        results = search.get_install_operation_by_id(operation_id)
        return results

#!/usr/bin/env python

import logging
import logging.config
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.decorators import results_message
from vFense.operations import *
from vFense.operations._constants import AgentOperations
from vFense.operations.search._db_agent_search import FetchAgentOperations
from vFense.core.agent import *
from vFense.errorz.status_codes import GenericCodes, GenericFailureCodes
from vFense.errorz._constants import ApiResultKeys
from vFense.plugins.patching import *
from vFense.plugins.patching.rv_db_calls import *
from vFense.utils.common import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class AgentOperationRetriever(object):
    def __init__(
        self, customer_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.DESC,
        sort_key=AgentOperationKey.CreatedTime,
        user_name=None, uri=None, method=None
        ):

        self.user_name = user_name
        self.customer_name = customer_name
        self.uri = uri
        self.method = method
        order_by_list = (
            [
                AgentOperationKey.Operation,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.CustomerName,
            ]
        )
        if sort_key in order_by_list:
            sort_key = sort_key
        else:
            sort_key = AgentOperationKey.CreatedTime

        self.agent_operations = (
            FetchAgentOperations(
                customer_name, count, offset,
                sort, sort_key
            )
        )

    @results_message
    def get_all(self, conn=None):
        count, data = self.agent_operations.fetch_all()
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

    @results_message
    def get_all_by_agentid(self, agent_id, conn=None):
        count, data = self.agent_operations.fetch_all_by_agentid(agent_id)
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


    @results_message
    def get_all_by_tagid(self, tag_id, conn=None):
        count, data = self.agent_operations.fetch_all_by_tagid(tag_id)
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


    @results_message
    def get_all_by_operation(self, operation):
        if operation in AgentOperations.OPERATIONS:
            generic_status_code = GenericCodes.InformationRetrieved
            count, data = (
                self.agent_operations.fetch_all_by_operation(operation)
            )
            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'

        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidId
            vfense_status_code = GenericFailureCodes.InvalidPlugin
            msg = 'operation is not valid'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


    @results_message
    def get_install_operation_by_id(self, operation_id, conn=None):
        generic_status_code = GenericCodes.InformationRetrieved
        count, data = (
            self.agent_operations.fetch_install_operation_by_id(operation_id)
        )

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

    @results_message
    def get_operation_by_id(self, operation_id, conn=None):
        generic_status_code = GenericCodes.InformationRetrieved
        count, data = (
            self.agent_operations.fetch_operation_by_id(operation_id)
        )

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

    def get_install_operation_for_email_alert(self, operation_id):
        count, data = (
            self.agent_operations.fetch_install_operation_for_email_alert(
                operation_id
            )
        )

        return(operations)


    def get_operation_for_email_alert(self, operation_id):
        count, data = (
            self.agent_operations.fetch_operation_for_email_alert(
                operation_id
            )
        )

        return(operations)

    def _set_results(self, gen_status_code, vfense_status_code,
                     msg, count, data):

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: gen_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: msg,
            ApiResultKeys.COUNT: count,
            ApiResultKeys.DATA: data,
            ApiResultKeys.USERNAME: self.user_name,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.method
        }

        return(results)

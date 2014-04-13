#!/usr/bin/env python

import logging
import logging.config
from vFense.db.client import db_create_close, r
from vFense.operations import OperationCollections, \
    OperationPerAgentIndexes, OperationPerAppIndexes

from vFense.core.decorators import return_status_tuple, time_it

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@time_it
@db_create_close
def fetch_agent_operation(operation_id, conn=None):
    """Fetch an operation by id and all of it's information
    Args:
        operation_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations._db import fetch_agent_operation
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> fetch_agent_operation(operation_id)

    Returns:
        Dictionary
        {
            "agents_expired_count": 0, 
            "cpu_throttle": "normal", 
            "agents_total_count": 1, 
            "plugin": "rv", 
            "tag_id": null, 
            "agents_completed_with_errors_count": 0, 
            "created_by": "admin", 
            "agents_pending_pickup_count": 0, 
            "completed_time": 1397246851, 
            "operation_status": 6006, 
            "agents_completed_count": 1, 
            "operation_id": "8fed3dc7-33d4-4278-9bd4-398a68bf7f22", 
            "created_time": 1397246674, 
            "agents_pending_results_count": 0, 
            "operation": "install_os_apps", 
            "updated_time": 1397246851, 
            "net_throttle": 0, 
            "agents_failed_count": 0, 
            "restart": "none", 
            "customer_name": "default"
        }
    """
    data = {}
    try:
        data = (
            r
            .table(OperationCollections.Agent)
            .get(operation_id)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def operation_with_agentid_exists(operation_id, agent_id, conn=None):
    """Verify if the operation exists by operation id and agent id.
    Args:
        operation_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations._db import operation_with_agentid_exists
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> operation_with_agentid_exists(operation_id, agent_id)

    Returns:
        Boolean True or False
    """
    exists = False
    try:
        is_empty = (
            r
            .table(OperationCollections.OperationPerAgent)
            .get_all(
                [operation_id, agent_id],
                index=OperationPerAgentIndexes.OperationIdAndAgentId
            )
            .is_empty()
            .run(conn)
        )
        if not is_empty:
            exists = True

    except Exception as e:
        logger.exception(e)

    return(exists)

@time_it
@db_create_close
def operation_with_agentid_and_appid_exists(
    operation_id, agent_id, app_id, conn=None
    ):
    """Verify if the operation exists by operation id, agent id and app id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID
        app_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations._db import operation_with_agentid_and_appid_exists
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
        >>> operation_with_agentid_and_appid_exists(operation_id, agent_id, app_id)

    Returns:
        Boolean True or False
    """
    exists = False
    try:
        is_empty = (
            r
            .table(OperationCollections.OperationPerApp)
            .get_all(
                [operation_id, agent_id, app_id],
                index=OperationPerAppIndexes.OperationIdAndAgentIdAndAppId
            )
            .is_empty()
            .run(conn)
        )
        if not is_empty:
            exists = True

    except Exception as e:
        logger.exception(e)

    return(exists)


@time_it
@db_create_close
@return_status_tuple
def insert_into_agent_operations(operation_data, conn=None):
    """Insert into agent_operations
        DO NOT CALL DIRECTLY
    Args:
        operation_data (list|dict): Insert a list of operations or an operation.

    Basic Usage:
        >>> from vFense.operations._db import insert_into_agent_operations
        >>> operation_id = {'opertion_id': 'id_goes_here'}
        >>> insert_into_agent_operations(operation_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(OperationCollections.Agent)
            .insert(operation_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

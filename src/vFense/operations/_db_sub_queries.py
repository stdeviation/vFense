#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.operations._db_model import (
    AgentOperationKey, OperationPerAgentKey
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class OperationMerge():
    TIMES = {
        AgentOperationKey.CompletedTime: (
            r.row[AgentOperationKey.CompletedTime].to_epoch_time()
        ),
        AgentOperationKey.CreatedTime: (
            r.row[AgentOperationKey.CreatedTime].to_epoch_time()
        )
    }

class OperationPerAgentMerge():
    TIMES = {
        OperationPerAgentKey.CompletedTime: (
            r.row[OperationPerAgentKey.CompletedTime].to_epoch_time()
        ),
        OperationPerAgentKey.ExpiredTime: (
            r.row[OperationPerAgentKey.ExpiredTime].to_epoch_time()
        ),
        OperationPerAgentKey.PickedUpTime: (
            r.row[OperationPerAgentKey.PickedUpTime].to_epoch_time()
        )
    }

import logging

from vFense._constants import VFENSE_LOGGING_CONFIG

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class HandOff(object):
    def __init__(self, agent_id=None, delete_afterwards=True):
        self.agent_id = agent_id
        self.delete_afterwards = delete_afterwards

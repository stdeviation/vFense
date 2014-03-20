import logging
import logging.config
from time import mktime
from datetime import datetime, timedelta

from vFense.receiver import *
from vFense.receiver._db import insert_into_agent_queue, \
    get_next_avail_order_id_in_agent_queue, get_agent_queue, \
    delete_job_in_queue, delete_multiple_jobs
from vFense.server._hierarchy import *
from vFense.server.hierarchy import *
from vFense.server.hierarchy import CoreProperty
from vFense.server.hierarchy.manager import Hierarchy

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class AgentQueue(object):
    def __init__(self, agent_id, customer_name):
        self.agent_id = agent_id
        self.customer_name = customer_name
        self.datetime_now = datetime.now()
        self.epoch_time_now = mktime(self.datetime_now.timetuple())
        self.global_expire_minutes = self.get_global_operation_ttl()

    def add(self, operation, expire_mins=None):
        """Add an operation to the agent_queue. If expire_mins is not passed,
        then we will use the global customer ttl value
        """

        if not expire_mins:
            expire_mins = self.global_expire_minutes

        operation[AgentQueueKey.AgentId] = self.agent_id
        operation[AgentQueueKey.CustomerName] = self.customer_name
        operation[AgentQueueKey.OrderId] = self._get_next_avail_order()
        operation[AgentQueueKey.CreatedTime] = self.epoch_time_now
        operation[AgentQueueKey.ExpireMinutes] = expire_mins
        operation[AgentQueueKey.ExpireTime] = self.get_expire_time(expire_mins)
        success = insert_into_agent_queue(operation)

        return(success)

    def _get_next_avail_order(self):
        """return the next available order_id from the database"""

        last_id = get_next_avail_order_id_in_agent_queue(self.agent_id)

        return(last_id + 1)

    def get_global_operation_ttl(self):
        """Return the global ttl property for a customer. ttl is in minutes"""

        ttl = (
            Hierarchy
            .get_customer_property(
                self.customer_name,
                CoreProperty.OperationTtl
            )
        )

        return(ttl)

    def get_expire_time(self, expire_mins):
        """return the expire_time, which is the current time + minutes"""

        expire_time = (
            mktime(
                (self.datetime_now + timedelta(minutes=expire_mins)).timetuple()
            )
        )

        return(expire_time)

    def get_agent_queue(self):
        """Return a list of jobs for an agent"""

        return(get_agent_queue(self.agent_id))

    def pop_agent_queue(self):
        """Return a list of jobs for an agent and then
        remove them from the queue"""

        job_ids = []
        agent_queue = get_agent_queue(self.agent_id)

        if agent_queue:
            for job_id in agent_queue:
                job_ids.append(job_id[AgentQueueKey.Id])

            delete_multiple_jobs(job_ids)

        return(agent_queue)

    def remove_job(self, job_id):
        """job_id is the primary key of the job you want to remove"""

        return(delete_job_in_queue(job_id))

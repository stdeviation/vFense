import logging
import logging.config
from time import mktime
from datetime import datetime, timedelta

from vFense.core.queue import *
from vFense.core.queue._db import insert_into_agent_queue, \
    get_next_avail_order_id_in_agent_queue, get_agent_queue, \
    delete_job_in_queue, delete_multiple_jobs

from vFense.core.customer.customers import get_customer_property
from vFense.core.customer import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class AgentQueue(object):
    def __init__(self, agent_id, customer_name):
        self.agent_id = agent_id
        self.customer_name = customer_name
        self.datetime_now = datetime.now()
        self.epoch_time_now = mktime(self.datetime_now.timetuple())
        self.global_server_queue_expire_minutes = (
            self.get_global_server_queue_ttl()
        )
        self.global_agent_queue_expire_minutes = (
            self.get_global_agent_queue_ttl()
        )

    def add(self, operation, expire_mins=None, agent_process_time=None):
        """Add an operation to the agent_queue. If expire_mins is not passed,
            then we will use the global customer ttl value.
        Args:
            operation (dict): the operation data.

        Kwargs:
            expire_mins (int): Minutes until operations is considered expired
                on the server.
            agent_process_time (float): Epoch seconds until the operation
                is considered expired before processing in the agent_queue

        Basic Usage:
            >>> from vFense.receiver.agent_queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> customer_name = 'default'
            >>> queue = AgentQueue(agent_id, customer_name)

        Returns:
            Boolean
        """

        if not expire_mins:
            expire_mins = self.global_server_queue_expire_minutes

        server_queue_ttl = self.get_queue_expire_time(expire_mins)

        if not agent_process_time:
            agent_expire_mins = (
                expire_mins + self.global_agent_queue_expire_minutes
            )
            agent_process_time  = (
                self.get_queue_expire_time(
                    agent_expire_mins
                )
            )

        elif agent_process_time:
            if agent_process_time <= server_queue_ttl:
                agent_expire_mins = (
                    expire_mins + self.global_agent_queue_expire_minutes
                )
                agent_process_time  = (
                    self.get_queue_expire_time(
                        agent_expire_mins
                    )
                )

        operation[AgentQueueKey.AgentId] = self.agent_id
        operation[AgentQueueKey.CustomerName] = self.customer_name
        operation[AgentQueueKey.OrderId] = self._get_next_avail_order()
        operation[AgentQueueKey.CreatedTime] = self.epoch_time_now
        operation[AgentQueueKey.ExpireMinutes] = expire_mins
        operation[AgentQueueKey.ServerQueueTTL] = server_queue_ttl
        operation[AgentQueueKey.AgentQueueTTL] = agent_process_time
        success = insert_into_agent_queue(operation)

        return(success)

    def _get_next_avail_order(self):
        """return the next available order_id from the database"""

        last_id = get_next_avail_order_id_in_agent_queue(self.agent_id)

        return(last_id + 1)

    def get_global_server_queue_ttl(self):
        """Return the global server ttl property for a customer.
            TTL is in minutes.
        """

        ttl = (
            get_customer_property(
                self.customer_name, CustomerKeys.ServerQueueTTL
            )
        )

        return(ttl)

    def get_global_agent_queue_ttl(self):
        """Return the global agent ttl property for a customer.
            TTL is in minutes.
        """

        ttl = (
            get_customer_property(
                self.customer_name, CustomerKeys.AgentQueueTTL
            )
        )

        return(ttl)

    def get_queue_expire_time(self, expire_mins):
        """return the expire_time, which is the current time + minutes
        Args:
            expire_mins (int): Minutes until operation is considered expired.
        Returns:
            float (expired time in epoch)
        """

        expire_time = (
            mktime(
                (self.datetime_now + timedelta(minutes=expire_mins)).timetuple()
            )
        )

        return(expire_time)

    def get_agent_queue(self):
        """Return a list of jobs for an agent
        Returns:
            List of dictionairies
            [
                {
                    "agent_queue_ttl": 1396778416, 
                    "plugin": "rv", 
                    "order_id": 1, 
                    "server_queue_ttl": 1396777816, 
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02", 
                    "created_time": 1396777216, 
                    "operation_id": "b95837d9-5df7-4ab0-9449-a7be196a2b12", 
                    "operation": "updatesapplications", 
                    "id": "f9817e07-6877-4857-aef3-e80f57022ac8", 
                    "expire_minutes": 10, 
                    "customer_name": "default"
                }
            ]
        """

        return(get_agent_queue(self.agent_id))

    def pop_agent_queue(self):
        """Return a list of jobs for an agent and then
            remove them from the queue
        Returns:
            List of dictionairies
            [
                {
                    "agent_queue_ttl": 1396778416, 
                    "plugin": "rv", 
                    "order_id": 1, 
                    "server_queue_ttl": 1396777816, 
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02", 
                    "created_time": 1396777216, 
                    "operation_id": "b95837d9-5df7-4ab0-9449-a7be196a2b12", 
                    "operation": "updatesapplications", 
                    "id": "f9817e07-6877-4857-aef3-e80f57022ac8", 
                    "expire_minutes": 10, 
                    "customer_name": "default"
                }
            ]
        """

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

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from time import mktime
from datetime import datetime, timedelta

from vFense.core.queue import AgentQueue
from vFense.core.queue._db_model import AgentQueueKey
from vFense.core.queue._db import (
    insert_into_agent_queue, get_next_avail_order_id_in_agent_queue,
    fetch_agent_queue, delete_job_in_queue, delete_multiple_jobs
)

from vFense.core.view._constants import DefaultViews
from vFense.core.view.manager import ViewManager

from vFense.core.queue.uris import get_agent_results_uri

from vFense.core.status_codes import DbCodes

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class AgentQueueManager(object):
    def __init__(self, agent_id, view_name=None):
        self.agent_id = agent_id
        self.datetime_now = datetime.now()
        self.epoch_time_now = mktime(self.datetime_now.timetuple())
        self.global_server_queue_expire_minutes = (
            self.get_global_server_queue_ttl(view_name)
        )
        self.global_agent_queue_expire_minutes = (
            self.get_global_agent_queue_ttl(view_name)
        )

    def add(self, operation, view_name, expire_mins=None,
            agent_process_time=None):
        """Add an operation to the agent_queue. If expire_mins is not passed,
            then we will use the global view ttl value.
        Args:
            operation (AgentQueueOperation instance): AgentQueueOperation instance.
            view_name (str): Name of the current view.

        Kwargs:
            expire_mins (int): Minutes until operations is considered expired
                on the server.
            agent_process_time (float): Epoch seconds until the operation
                is considered expired before processing in the agent_queue

        Basic Usage:
            >>> from vFense.receiver.agent_queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> view_name = 'global'
            >>> operation = {'valid_operation': 'data'}
            >>> queue = AgentQueueManager(agent_id)
            >>> queue.add(operation, view_name)

        Returns:
            Boolean
        """
        self.global_server_queue_expire_minutes = (
            self.get_global_server_queue_ttl(view_name)
        )
        self.global_agent_queue_expire_minutes = (
            self.get_global_agent_queue_ttl(view_name)
        )
        success = False
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
        request_method, response_uri = (
            get_agent_results_uri(
                self.agent_id,
                operation.operation
            )
        )
        agent_queue = AgentQueue()
        agent_queue.agent_id = self.agent_id
        agent_queue.view_name = view_name
        agent_queue.request_method = request_method
        agent_queue.response_uri = response_uri
        agent_queue.order_id = self._get_next_avail_order()
        agent_queue.created_time = self.epoch_time_now
        agent_queue.expire_minutes = expire_mins
        agent_queue.server_queue_ttl = server_queue_ttl
        agent_queue.agent_queue_ttl = agent_process_time
        agent_queue.operation = operation.to_dict()
        status_code, count, error, generated_ids = (
            insert_into_agent_queue(agent_queue.to_dict_db())
        )

        if status_code == DbCodes.Inserted:
            success = True

        return(success)

    def _get_next_avail_order(self):
        """return the next available order_id from the database

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> queue = AgentQueueManager(agent_id)
            >>> queue._get_next_avail_order()

        Returns:
            Integer
        """

        last_id = get_next_avail_order_id_in_agent_queue(self.agent_id)

        return(last_id + 1)

    def get_global_server_queue_ttl(self, view_name):
        """Return the global server ttl property for a view.
            TTL is in minutes.
        Args:
            view_name (str): Name of the current view.

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> view_name = 'global'
            >>> queue = AgentQueueManager(agent_id)
            >>> queue.get_global_server_queue_ttl(view_name)

        Returns:
            Integer
        """
        if view_name:
            ttl = ViewManager(view_name).properties.server_queue_ttl
        else:
            ttl = ViewManager(DefaultViews.GLOBAL).properties.server_queue_ttl

        return(ttl)

    def get_global_agent_queue_ttl(self, view_name):
        """Return the global agent ttl property for a view.
            TTL is in minutes.
        Args:
            view_name (str): Name of the current view.

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> view_name = 'global'
            >>> queue = AgentQueueManager(agent_id)
            >>> queue.get_global_agent_queue_ttl(view_name)

        Returns:
            Integer
        """
        if view_name:
            ttl = ViewManager(view_name).properties.agent_queue_ttl
        else:
            ttl = ViewManager(DefaultViews.GLOBAL).properties.agent_queue_ttl

        return(ttl)

    def get_queue_expire_time(self, expire_mins):
        """return the expire_time, which is the current time + minutes
        Args:
            expire_mins (int): Minutes until operation is considered expired.

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> queue = AgentQueueManager(agent_id)
            >>> expire_mins = 10
            >>> queue.get_queue_expire_time(expire_mins)

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

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> queue = AgentQueueManager(agent_id)
            >>> queue.fetch_agent_queue()

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
                    "view_name": "global"
                }
            ]
        """

        return(fetch_agent_queue(self.agent_id))

    def pop_agent_queue(self):
        """Return a list of jobs for an agent and then
            remove them from the queue

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> queue = AgentQueueManager(agent_id)
            >>> queue.pop_agent_queue()

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
                    "view_name": "global"
                }
            ]
        """

        job_ids = []
        agent_queue = fetch_agent_queue(self.agent_id)

        if agent_queue:
            for job_id in agent_queue:
                job_ids.append(job_id[AgentQueueKey.Id])

            delete_multiple_jobs(job_ids)

        return(agent_queue)

    def remove_job(self, job_id):
        """Delete a job in the queue
        Args:
            job_id (str): The 36 character job UUID.

        Basic Usage:
            >>> from vFense.queue.queue import AgentQueue
            >>> agent_id = '70f3ca5f-09aa-4233-80ad-8fa5da6695fe'
            >>> queue = AgentQueueManager(agent_id)
            >>> job_id = 'd4119b36-fe3c-4973-84c7-e8e3d72a3e02'
            >>> queue.remove_job(job_id)

        """
        success = False
        status_code, count, error, generated_ids = (
            delete_job_in_queue(job_id)
        )
        if status_code == DbCodes.Deleted:
            success = True

        return(success)

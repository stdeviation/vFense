import tornado.httpserver
import simplejson as json

import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request
)
from utils.common import *
from datetime import datetime

from jsonpickle import encode

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class AgentsOsQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_os_details(username=username, view_name=view_name,
                    key=key,query=query, uri=uri, method=method)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsHardwareQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_hardware_details(username=username, view_name=view_name,
                    key=key, query=query,
                    uri=uri, method=method)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsCPUQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_cpu_details(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsMemoryQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_memory_stats(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method,
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsDiskQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_disk_stats(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsNetworkQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_network_details(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsLastUpdatedHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_last_updated(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class AgentsRequireRebootHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_reboot_pending(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class AgentsConnectionStatusHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        view_name = get_current_view_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_status(username=username, view_name=view_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    Results(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


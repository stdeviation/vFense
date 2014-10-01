import os
import sys
import importlib
import inspect
import traceback

from vFense.receiver.api.core.newagent import NewAgentV1, NewAgentV2
from vFense.receiver.api.core.checkin import CheckInV1, CheckInV2
from vFense.receiver.api.core.startup import StartUpV1, StartUpV2
from vFense.receiver.api.core.generics import ValidateToken
from vFense.receiver.api.core.result_uris import (
    ResultURIs, AgentResultURIs, ResultURIsV2, AgentResultURIsV2
)
from vFense.receiver.api.core.results import (
    RebootResultsV1, ShutdownResultsV1, RebootResultsV2, ShutdownResultsV2
)

from vFense.core.api.base import (
    RootHandler, RvlLoginHandler, RvlLogoutHandler, Authentication
)
from vFense.core.api.user import UserHandler, UsersHandler
from vFense.core.api.group import GroupHandler, GroupsHandler
from vFense.core.api.view import ViewHandler, ViewsHandler
from vFense.core.api.tag import TagHandler, TagsHandler
from vFense.core.api.scheduler import (
    JobHandler, JobsHandler, TimeZonesHandler
)
from vFense.core.api.agent import (
    AgentHandler, AgentsHandler, AgentTagHandler,
    FetchSupportedOperatingSystems, FetchValidEnvironments
)
from vFense.core.api.base import (
    RootHandler, LoginHandler, LogoutHandler, WebSocketHandler, AdminHandler
)


from vFense.receiver.api.rv.results import (
    InstallOsAppsResults, InstallCustomAppsResults,
    InstallSupportedAppsResults, InstallAgentAppsResults,
    UninstallAppsResults
)

from vFense.receiver.api.rv.app_results import (
    AppsResultsV2, CustomAppsResultsV2,
    SupportedAppsResultsV2, vFenseAppsResultsV2,
    UninstallResultsV2
)
from vFense.receiver.api.rv.updateapplications import UpdateApplicationsV1
from vFense.receiver.api.rv.refresh_apps import RefreshAppsV2
from vFense.receiver.api.rv.agent_update import (
    AgentUpdateHandler, AgentUpdateHandlerV2
)

from vFense.core.api.email_api import CreateEmailConfigHandler, \
    GetEmailConfigHandler
from vFense.core.api.log_api import LoggingModifyerHandler, \
    LoggingListerHandler
from vFense.core.api.reports_api import (AgentsOsDetailsHandler,
    AgentsHardwareDetailsHandler, AgentsCPUDetailsHandler,
    AgentsMemoryDetailsHandler, AgentsDiskDetailsHandler,
    AgentsNetworkDetailsHandler)

from vFense.plugins.patching.api.os_apps import (
    AgentIdAppsHandler, TagIdAppsHandler, AppIdAppsHandler,
    GetAgentsByAppIdHandler, AppsHandler, UploadHandler
)
from vFense.plugins.patching.api.stats_api import (AgentSeverityHandler,
    AgentOsAppsOverTimeHandler, TagSeverityHandler, TagOsAppsOverTimeHandler,
    TagStatsByOsHandler)

from vFense.core.api.agent_operations import (
    AgentOperationsHandler, TagOperationsHandler
)


class CoreLoader():

    def get_core_listener_api_handlers(self):
        handlers = [
            #v1 APIS
            #Login and Logout Operations
            (r"/rvl/?", RootHandler),
            (r"/rvl/login/?", RvlLoginHandler),
            (r"/rvl/logout/?", RvlLogoutHandler),
            (r"/rvl/validate?", ValidateToken),

            #Operations for the New Core Plugin
            (r"/rvl/v1/core/newagent/?", NewAgentV1),
            (r"/rvl/v1/core/uris/response?", ResultURIs),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/startup/?",
                StartUpV1),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/uris/response/?",
                ResultURIs),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/checkin/?",
                CheckInV1),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/reboot/?",
                RebootResultsV1),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/shutdown/?",
                ShutdownResultsV1),

            #Patching Plugin
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/updatesapplications/?", UpdateApplicationsV1),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/available_agent_update/?", AgentUpdateHandler),

            #New Operations for the New RV Plugin
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/os?", InstallOsAppsResults),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/custom?", InstallCustomAppsResults),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/supported?", InstallSupportedAppsResults),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/agent?", InstallAgentAppsResults),
            (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/uninstall?", UninstallAppsResults),


            #v2 APIS for applications results
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/os?", AppsResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/custom?", CustomAppsResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/supported?", SupportedAppsResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/agent?", vFenseAppsResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/uninstall?", UninstallResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/refresh_apps/?", RefreshAppsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/available_agent_update/?", AgentUpdateHandlerV2),


            #v2 APIS
            #Operations for the New Core Plugin
            (r"/rvl/v2/core/newagent/?", NewAgentV2),
            (r"/rvl/v2/core/validate_token/?", ValidateToken),
            (r"/rvl/v2/core/uris/response?", ResultURIsV2),
            (r"/rvl/v2/apps/available_agent_update/?", AgentUpdateHandlerV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/startup", StartUpV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/uris/response/?", ResultURIsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/checkin/?", CheckInV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/reboot/?", RebootResultsV2),
            (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/shutdown/?", ShutdownResultsV2)

        ]

        return handlers

    def get_core_web_api_handlers(self):
        handlers = [

            (r"/?", RootHandler),
            (r"/login/?", LoginHandler),
            (r"/logout/?", LogoutHandler),
            #(r"/ws/?", WebSocketHandler),
            (r"/adminForm", AdminHandler),
            (r"/api/v1/authenticated?", Authentication),

            ##### New User API
            (r"/api/v1/user/([a-zA-Z0-9_ ]+)?", UserHandler),
            (r"/api/v1/users?", UsersHandler),

            ##### New Group API
            (r"/api/v1/group/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", GroupHandler),
            (r"/api/v1/groups?", GroupsHandler),

            ##### New View API
            (r'/api/v1/view/((?:\w(?!%20+")|%20(?!%20*")){1,36})?', ViewHandler),
            (r"/api/v1/views?", ViewsHandler),

            ##### Email API Handlers
            (r"/api/email/config/create?", CreateEmailConfigHandler),
            (r"/api/email/config/list?", GetEmailConfigHandler),

            ##### Logger API Handlers
            (r"/api/logger/modifyLogging?", LoggingModifyerHandler),
            (r"/api/logger/getParams?", LoggingListerHandler),

            ##### Reports Api
            (r"/api/v1/reports/osdetails?", AgentsOsDetailsHandler),
            (r"/api/v1/reports/hardwaredetails?",AgentsHardwareDetailsHandler),
            (r"/api/v1/reports/cpudetails?",AgentsCPUDetailsHandler),
            (r"/api/v1/reports/memorydetails?",AgentsMemoryDetailsHandler),
            (r"/api/v1/reports/diskdetails?",AgentsDiskDetailsHandler),
            (r"/api/v1/reports/networkdetails?",AgentsNetworkDetailsHandler),

            ##### Scheduler API Handlers
            (r"/api/v1/schedules?", JobsHandler),
            (r"/api/v1/schedule/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", JobHandler),
            #(r"/api/v1/schedules/recurrent/none?", SchedulerDateBasedJobHandler),
            #(r"/api/v1/schedules/recurrent/daily?", SchedulerDailyRecurrentJobHandler),
            #(r"/api/v1/schedules/recurrent/monthly?", SchedulerMonthlyRecurrentJobHandler),
            #(r"/api/v1/schedules/recurrent/yearly?", SchedulerYearlyRecurrentJobHandler),
            #(r"/api/v1/schedules/recurrent/weekly?", SchedulerWeeklyRecurrentJobHandler),
            #(r"/api/v1/schedules/recurrent/custom?", SchedulerCustomRecurrentJobHandler),

            ##### Agent API Handlers
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", AgentHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/bar/severity?",AgentSeverityHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/column/range/apps/os?", AgentOsAppsOverTimeHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/tag?", AgentTagHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/(os|agentupdates|custom|supported)?", AgentIdAppsHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/operations?", AgentOperationsHandler),
            (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/uris/response?", AgentResultURIs),

            ##### Agents API Handlers
            (r"/api/v1/agents", AgentsHandler),

            ##### Tag API Handlers
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", TagHandler),
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/bar/severity?",TagSeverityHandler),
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/column/range/apps/os?", TagOsAppsOverTimeHandler),
            #(r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/linear/severity?",TagPackageSeverityOverTimeHandler),
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/(os|agentupdates|supported|custom)?", TagIdAppsHandler),
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/operations?", TagOperationsHandler),
            (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/stats_by_os?", TagStatsByOsHandler),

            ##### Tags API Handlers
            (r"/api/v1/tags", TagsHandler),

            ##### Generic API Handlers
            (r"/api/v1/supported/operating_systems?", FetchSupportedOperatingSystems),
            (r"/api/v1/supported/environments?", FetchValidEnvironments),
            (r"/api/v1/supported/timezones?", TimeZonesHandler),
            #(r"/api/package/getDependecies?", GetDependenciesHandler),

            ##### Apps API Handlers
            (r"/api/v1/app/(os|supported|agentupdates|)/([0-9A-Za-z]{64})?", AppIdAppsHandler),
            (r"/api/v1/app/(os|supported|agentupdates)/([0-9A-Za-z]{64})/agents?", GetAgentsByAppIdHandler),
            (r"/api/v1/apps/(os|supported|agentupdates)", AppsHandler),
            (r"/api/v1/apps/upload?", UploadHandler),

        ]

        return handlers


class PluginsLoader():
    """Used to retrieve the listener and web api's from every plugin."""

    def __init__(self):
        """Append the plugins directory to sys path."""
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.plugins_dir = 'plugins'
        self.plugins_path = os.path.join(self.curr_dir, self.plugins_dir)

        sys.path.append(self.plugins_path)

    def _get_all_plugins(self):
        """Search through the plugins directory and find all directories
        with an __init__.py file. These directories will be considered
        plugins.

        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> plugins = loader._get_all_plugins()
            >>> print plugins
            >>> ['plugins.patching', 'plugins.monit', ...]

        Returns:
            (list str) - A list of modules as strings corresponding to found
                plugins.

                Ex: ['plugins.patching', 'plugins.monit', ...]
        """
        plugins = []

        for entry in os.listdir(self.plugins_path):
            entry_path = os.path.join(self.plugins_path, entry)
            init_path = os.path.join(entry_path, '__init__.py')

            if os.path.isdir(entry_path) and os.path.exists(init_path):
                module = os.path.join(
                    self.plugins_dir, entry
                ).replace('/', '.')

                plugins.append(module)

        return plugins

    def _import_all_plugins(self, plugins):
        """Imports the modules given.

        Args:
            plugins (list): A list of modules as strings corresponding to
                plugins.

                Ex: ['plugins.patching', 'plugins.monit', ...]

        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> imported = loader._import_all_plugins(plugins)
            >>> print imported
            >>> [<module 'plugins.monit' from 'plugins/monit/__init__.pyc'>]

        Returns:
            (list): A list of loaded modules.

            Ex: [<module 'plugins.monit' from 'plugins/monit/__init__.pyc'>]
        """
        imported_plugins = []

        for module in plugins:
            try:
                imported_plugins.append(importlib.import_module(module))
            except Exception as e:
                print "Failed to import {0} because of: {1}".format(
                    module, e
                )

                continue

        return imported_plugins

    def get_plugins_listener_api_handlers(self):
        """Retrieves the listener handlers from every plugin by calling the
        get_listener_api_handlers function of every plugin found.

        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> loader.get_plugins_listener_api_handlers()

        Returns:
            (list) - Returns a list of tuples where the first element is
                the regex to be handled and the second element is
                the class that will be used to handle that regex.

            Ex:
                [('/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/monitoring/monitordata/?',
                <class 'vFense.plugins.monit.api_handlers.UpdateMonitoringStatsV1'>)]

        """

        plugins = self._get_all_plugins()
        imported_plugins = self._import_all_plugins(plugins)

        handlers = []
        for plugin in imported_plugins:
            try:
                if 'get_listener_api_handlers' in plugin.__dict__.keys():
                    handlers.extend(plugin.get_listener_api_handlers())

            except Exception as e:
                print "Failed to get listener handlers: {0}".format(e)
                print traceback.format_exc()

        return handlers

    def get_plugins_web_api_handlers(self):
        """Retrieves the listener handlers from every plugin by calling the
        get_plugins_web_api_handlers function of every plugin found.

        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> loader.get_plugins_web_api_handlers()

        Returns:
            (list) - Returns a list of tuples where the first element is
                the regex to be handled and the second element is
                the class that will be used to handle that regex.

            Ex:
                [('/api/monitor/memory/?', <class 'vFense.plugins.monit.api_handlers.GetMemoryStats'>),
                ('/api/monitor/filesystem/?', <class 'vFense.plugins.monit.api_handlers.GetFileSystemStats'>)]

        """
        plugins = self._get_all_plugins()
        imported_plugins = self._import_all_plugins(plugins)

        handlers = []
        for plugin in imported_plugins:
            try:
                if 'get_web_api_handlers' in plugin.__dict__.keys():
                    handlers.extend(plugin.get_web_api_handlers())

            except Exception as e:
                print "Failed to get web handlers: {0}".format(e)
                print traceback.format_exc()

        return handlers

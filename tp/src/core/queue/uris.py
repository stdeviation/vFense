import os
from vFense.core._constants import HTTPMethods, CommonKeys
from vFense.operations._constants import ValidOperations, ListenerURIs, \
    AuthenticationOperations, AuthenticationURIs, BaseURIs

from vFense.core.agent import AgentKey
from vFense.core.agent.agents import get_agent_info
from vFense.core.decorators import results_message, time_it
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import *

@time_it
def get_agent_results_uri(agent_id, operation):
    """Return back the http method and response uri for an operation.
    Args:
        agent_id (str): 36 character UUID
        operation (str): valid vFense operation.

    Basic Usage:
        >>> from vFense.receiver.agent_uris import get_agent_results_uri
        >>> agent_id = 'd4119b36-fe3c-4973-84c7-e8e3d72a3e02'
        >>> operation = 'install_os_apps'
        >>> get_agent_results_uri(agent_id, operation)

    Returns:
        Tuple
        ('put', 'rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/reboot')

    """

    result_uris = {

        ValidOperations.INSTALL_OS_APPS: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.INSTALL_OS_APPS
            )
        ),

        ValidOperations.INSTALL_CUSTOM_APPS: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.INSTALL_CUSTOM_APPS
            )
        ),

        ValidOperations.INSTALL_SUPPORTED_APPS: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.INSTALL_SUPPORTED_APPS
            )
        ),

        ValidOperations.INSTALL_AGENT_APPS: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.INSTALL_AGENT_APPS
            )
        ),

        ValidOperations.UNINSTALL: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.UNINSTALL
            )
        ),

        ValidOperations.UNINSTALL_AGENT: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.UNINSTALL
            )
        ),

        ValidOperations.REBOOT: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.REBOOT
            )
        ),

        ValidOperations.SHUTDOWN: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.SHUTDOWN
            )
        ),

        ValidOperations.CHECK_IN: (
            HTTPMethods.GET,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.CHECK_IN
            )
        ),

        ValidOperations.MONITOR_DATA: (
            HTTPMethods.GET,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.MONITOR_DATA
            )
        ),

        ValidOperations.START_UP: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.START_UP
            )
        ),

        ValidOperations.APPS_REFRESH: (
            HTTPMethods.PUT,
            os.path.join(
                BaseURIs.LISTENER, agent_id, ListenerURIs.APPS_REFRESH
            )
        ),

        ValidOperations.NEWAGENT: (
            HTTPMethods.POST,
            os.path.join(
                BaseURIs.LISTENER, ListenerURIs.NEWAGENT
            )
        ),

        ValidOperations.RA: (
            HTTPMethods.POST,
            os.path.join(BaseURIs.LISTENER, ListenerURIs.RA)
        )
    }

    return result_uris.get(operation, ())


@time_it
@results_message
def get_result_uris(agent_id, user_name=None, uri=None, method=None):
    """Returns back a dictionary with all of the agent api calls for an agent.
    Args:
        agent_id (str): 36 character UUID

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.receiver.agent_uris import get_result_uris
        >>> agent_id = 'd4119b36-fe3c-4973-84c7-e8e3d72a3e02'
        >>> get_result_uris(agent_id)

    Returns:
        Dictionary
        {
            "count": 1,
            "uri": null,
            "rv_status_code": 1001,
            "http_method": null,
            "http_status": 200,
            "message": "None - data was retrieved",
            "data": {
                "check_in": {
                    "response_uri": "rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/checkin",
                    "request_method": "GET"
                },  
                "startup": {
                    "response_uri": "rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/startup",
                    "request_method": "PUT"
                },
                "shutdown": {
                    "response_uri": "rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/shutdown",
                    "request_method": "PUT"
                },
            }
        }
    """
    base = os.path.join(BaseURIs.LISTENER, agent_id)
    status_code = 0
    status = get_result_uris.func_name + ' - '
    result_uris = {
        AuthenticationOperations.LOGIN: {
            CommonKeys.RESPONSE_URI: AuthenticationURIs.LOGIN,
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST
        },
        AuthenticationOperations.LOGOUT: {
            CommonKeys.RESPONSE_URI: AuthenticationURIs.LOGOUT,
            CommonKeys.REQUEST_METHOD: HTTPMethods.GET
        },
        ValidOperations.NEWAGENT: {
            CommonKeys.RESPONSE_URI: os.path.join(
                BaseURIs.LISTENER, ListenerURIs.NEWAGENT
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST
        },
        ValidOperations.RA: {
            CommonKeys.RESPONSE_URI: os.path.join(
                BaseURIs.LISTENER, ListenerURIs.RA
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST
        },
        ValidOperations.APPS_REFRESH: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.APPS_REFRESH
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.CHECK_IN: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.CHECK_IN
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.GET
        },
        ValidOperations.START_UP: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.START_UP
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.REBOOT: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.REBOOT
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
         },
        ValidOperations.SHUTDOWN: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.SHUTDOWN
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.INSTALL_OS_APPS: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.INSTALL_OS_APPS
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.INSTALL_CUSTOM_APPS: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.INSTALL_CUSTOM_APPS
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.INSTALL_SUPPORTED_APPS: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.INSTALL_SUPPORTED_APPS
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.INSTALL_AGENT_APPS: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.INSTALL_AGENT_APPS
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        },
        ValidOperations.UNINSTALL: {
            CommonKeys.RESPONSE_URI: os.path.join(
                base, ListenerURIs.UNINSTALL
            ),
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT
        }
    }

    agent_exist = get_agent_info(agent_id, AgentKey.AgentId)
    if agent_exist:
        generic_status_code = GenericCodes.InformationRetrieved
        vfense_status_code = GenericCodes.InformationRetrieved
        msg = 'response uris retrieved successfully for agent_id %s' % \
              (agent_id)
        count = 1

    elif agent_exist:
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist
        result_uris = {}
        msg = 'invalid agent_id %s' % (agent_id)
        count = 0

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.COUNT: count,
        ApiResultKeys.DATA: result_uris,
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)

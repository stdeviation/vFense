import os
from vFense.core._constants import HTTPMethods
from vFense.core.queue._constants import *

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
        ('put', '/rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/reboot/?')

    """
    if operation == ValidOperations.INSTALL_OS_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.INSTALL_OS_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_CUSTOM_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.INSTALL_CUSTOM_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_SUPPORTED_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.INSTALL_SUPPORTED_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_AGENT_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.INSTALL_AGENT_APPS
            )
        )

    elif operation == ValidOperations.UNINSTALL:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.UNINSTALL
            )
        )

    elif operation == ValidOperations.UNINSTALL_AGENT:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.UNINSTALL
            )
        )

    elif operation == ValidOperations.REBOOT:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.REBOOT
            )
        )

    elif operation == ValidOperations.SHUTDOWN:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.SHUTDOWN
            )
        )

    elif operation == ValidOperations.CHECKIN:
        request_method = HTTPMethods.GET
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.CHECKIN
            )
        )

    elif operation == ValidOperations.STARTUP:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.START_UP
            )
        )

    elif operation == ValidOperations.APPS_REFRESH:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + AgentListenerURIs.APPS_REFRESH
            )
        )

    elif operation == ValidOperations.NEWAGENT:
        request_method = HTTPMethods.POST
        response_uri = (
            BaseURIs.LISTENER + ListenerURIs.NEWAGENT[1:]
        )

    elif operation == ValidOperations.RA:
        request_method = HTTPMethods.POST
        response_uri = (
            BaseURIs.LISTENER + ListenerURIs.RA[1:]
        )


    return(request_method, response_uri)


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
                "checkin": {
                    "response_uri": "/rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/checkin/?",
                    "request_method": "PUT"
                },  
                "startup": {
                    "response_uri": "/rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/startup/?",
                    "request_method": "PUT"
                },
                "shutdown": {
                    "response_uri": "/rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/shutdown/?",
                    "request_method": "PUT"
                },
            }
        }
    """
    base = BaseURIs.LISTENER + agent_id
    status_code = 0
    status = get_result_uris.func_name + ' - '
    result_uris = {
        AuthenticationOperations.LOGIN: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST,
            CommonKeys.RESPONSE_URI: AuthenticationURIs.LOGIN
        },
        AuthenticationOperations.LOGOUT: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.GET,
            CommonKeys.RESPONSE_URI: AuthenticationURIs.LOGOUT
        },
        ValidOperations.NEWAGENT: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST,
            CommonKeys.RESPONSE_URI: BaseURIs.LISTENER[:-1] + ListenerURIs.NEWAGENT
        },
        ValidOperations.RA: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.POST,
            CommonKeys.RESPONSE_URI: BaseURIs.LISTENER[:-1] + ListenerURIs.NEWAGENT
        },
        ValidOperations.APPS_REFRESH: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.APPS_REFRESH
        },
        ValidOperations.CHECKIN: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.CHECKIN
        },
        ValidOperations.STARTUP: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.STARTUP
        },
        ValidOperations.REBOOT: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.REBOOT
         },
        ValidOperations.SHUTDOWN: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.SHUTDOWN
        },
        ValidOperations.INSTALL_OS_APPS: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.INSTALL_OS_APPS
        },
        ValidOperations.INSTALL_CUSTOM_APPS: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.INSTALL_CUSTOM_APPS
        },
        ValidOperations.INSTALL_SUPPORTED_APPS: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.INSTALL_SUPPORTED_APPS
        },
        ValidOperations.INSTALL_AGENT_APPS: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.INSTALL_AGENT_APPS
        },
        ValidOperations.UNINSTALL: {
            CommonKeys.REQUEST_METHOD: HTTPMethods.PUT,
            CommonKeys.RESPONSE_URI: base + AgentListenerURIs.UNINSTALL
        }
    }

    agent_exist = get_agent_info(agent_id, AgentKey.AgentId)
    if agent_exist:
        generic_status_code = GenericCodes.InformationRetrieved
        vfense_status_code = GenericCodes.InformationRetrieved
        msg = 'response uris retrieved successfully for agent_id %s' % (agent_id)
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

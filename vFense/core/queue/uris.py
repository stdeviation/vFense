import os
from vFense.core._constants import CommonKeys
from vFense.core.operations._constants import (
    BaseURIs, URIVersions, V2ListenerURIs, V1ListenerURIs,
    AuthenticationOperations
)

from vFense.core.decorators import time_it
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes


def _get_result_uris_dict(version, agent_id=None):

    results = {}
    if version == URIVersions.V2:
        base_without_agentid = os.path.join(BaseURIs.LISTENER, URIVersions.V2)
        if agent_id:
            base = (
                os.path.join(BaseURIs.LISTENER, URIVersions.V2, agent_id)
            )
        else:
            base = (
                os.path.join(BaseURIs.LISTENER, URIVersions.V2, '{0}')
            )
        for uri in V2ListenerURIs.get_valid_listener_uris():
            if uri[3]:
                results[uri[0]] = {
                    CommonKeys.RESPONSE_URI: os.path.join(base, uri[1]),
                    CommonKeys.REQUEST_METHOD: uri[2],
                }
            else:
                results[uri[0]] = {
                    CommonKeys.RESPONSE_URI: (
                        os.path.join(base_without_agentid, uri[1])
                    ),
                    CommonKeys.REQUEST_METHOD: uri[2],
                }

    elif version == URIVersions.V1:
        base_without_agentid = os.path.join(BaseURIs.LISTENER, URIVersions.V1)
        base_without_version = BaseURIs.LISTENER
        if agent_id:
            base = (
                os.path.join(BaseURIs.LISTENER, URIVersions.V1, agent_id)
            )
        else:
            base = (
                os.path.join(BaseURIs.LISTENER, URIVersions.V1, '{0}')
            )
        for uri in V1ListenerURIs.get_valid_listener_uris():
            if (not uri[3] and AuthenticationOperations.LOGIN or
                    not uri[3] and AuthenticationOperations.LOGOUT):

                results[uri[0]] = {
                    CommonKeys.RESPONSE_URI: (
                        os.path.join(base_without_version, uri[1])
                    ),
                    CommonKeys.REQUEST_METHOD: uri[2],
                }
            elif uri[3]:

                results[uri[0]] = {
                    CommonKeys.RESPONSE_URI: (
                        os.path.join(base, uri[1])
                    ),
                    CommonKeys.REQUEST_METHOD: uri[2],
                }
            else:
                results[uri[0]] = {
                    CommonKeys.RESPONSE_URI: (
                        os.path.join(base_without_agentid, uri[1])
                    ),
                    CommonKeys.REQUEST_METHOD: uri[2],
                }

    return results


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
        ('PUT', 'rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/reboot')

    """

    result_uri_dict = _get_result_uris_dict(agent_id).get(operation, {})

    if result_uri_dict:
        return (
            result_uri_dict[CommonKeys.RESPONSE_URI],
            result_uri_dict[CommonKeys.REQUEST_METHOD]
        )

    return ('', '')



@time_it
def get_result_uris(agent_id=None, version='v2'):
    """Returns back a dictionary with all of the agent api calls for an agent.
    Kwargs:
        agent_id (str): 36 character UUID of the agent.
            default=None
        version (str): v1, v2, etc...
            default=v1

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
    result_uris = _get_result_uris_dict(version, agent_id)
    results = ApiResults()
    results.fill_in_defaults()
    results.generic_status_code = GenericCodes.InformationRetrieved
    results.vfense_status_code = GenericCodes.InformationRetrieved
    results.message = 'response uris retrieved successfully.'
    results.count = 1
    results.data = result_uris
    return results

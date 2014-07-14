import logging, logging.config
from ast import literal_eval
import json
from functools import wraps


from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResultKeys
from vFense.receiver.results import (
    AgentResults
)
from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes,
)
from vFense.core.view.status_codes import (
    ViewCodes, ViewFailureCodes
)
from vFense.receiver.status_codes import (
    AgentResultCodes, AgentFailureResultCodes
)
from vFense.core.agent.status_codes import (
    AgentCodes
)
from vFense.core.agent.manager import AgentManager
from vFense.core.agent._db_model import AgentKeys
from vFense.core.view._db import (
    token_exist_in_current, token_exist_in_previous
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vFense_stats')


def authenticate_agent(fn):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        results = (
            {
                ApiResultKeys.URI: self.request.uri,
                ApiResultKeys.HTTP_STATUS_CODE: 403,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.AuthorizationDenied
                ),
                ApiResultKeys.HTTP_METHOD: self.request.method,
            }
        )
        try:
            auth_headers = (
                literal_eval(self.request.headers.get('Authentication'))
            )
            token = auth_headers.get('token')
            agent_id = auth_headers.get('agent_id')
            if token and agent_id:
                authenticated = token_exist_in_current(token)
                valid_old_token = token_exist_in_previous(token)
                agent = AgentManager(agent_id)
                if agent.properties:
                    enabled = agent.get_attribute(AgentKeys.Enabled)
                    assign_new_token = (
                        agent.get_attribute(AgentKeys.AssignNewToken)
                    )
                    if enabled and authenticated:
                        agent.update_token(token)
                        return fn(self, *args, **kwargs)

                    elif enabled and valid_old_token and assign_new_token:
                        agent.update_token(token)
                        agent.assign_new_token(False)
                        return fn(self, *args, **kwargs)

                    elif enabled and valid_old_token and not assign_new_token:
                        agent.update_token(token)
                        msg = '{0} is a previous token'.format(token)
                        results[ApiResultKeys.INVALID_ID] = token
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            ViewCodes.ValidPreviousToken
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        self.set_status(
                            results[ApiResultKeys.HTTP_STATUS_CODE]
                        )
                        self.write(json.dumps(results, indent=4))

                    elif not authenticated and not valid_old_token:
                        msg = '{0} is not a valid token'.format(token)
                        results[ApiResultKeys.INVALID_ID] = token
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            ViewFailureCodes.InvalidToken
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        self.set_status(
                            results[ApiResultKeys.HTTP_STATUS_CODE]
                        )
                        self.write(json.dumps(results, indent=4))

                    elif not agent.get_attribute(AgentKeys.Enabled):
                        msg = '{0} is disabled'.format(agent_id)
                        results[ApiResultKeys.AGENT_ID] = agent_id
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            AgentCodes.Disabled
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        self.set_status(
                            results[ApiResultKeys.HTTP_STATUS_CODE]
                        )
                        self.write(json.dumps(results, indent=4))

                else:
                    msg = '{0} not a valid agent id'.format(agent_id)
                    results[ApiResultKeys.AGENT_ID] = agent_id
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.AgentIdDoesNotExist
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    self.set_status(
                        results[ApiResultKeys.HTTP_STATUS_CODE]
                    )
                    self.write(json.dumps(results, indent=4))

            else:
                msg = 'Headers do not contain Authentication information'
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidHeaders
                )
                results[ApiResultKeys.MESSAGE] = msg
                self.set_status(
                    results[ApiResultKeys.HTTP_STATUS_CODE]
                )
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            msg = e
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.SomethingBroke
            )
            self.set_status(
                results[ApiResultKeys.HTTP_STATUS_CODE]
            )
            self.write(json.dumps(results, indent=4))

    return wrapper

def authenticate_token(fn):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        results = (
            {
                ApiResultKeys.URI: self.request.uri,
                ApiResultKeys.HTTP_STATUS_CODE: 403,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.AuthorizationDenied
                ),
                ApiResultKeys.HTTP_METHOD: self.request.method,
            }
        )
        try:
            auth_headers = (
                literal_eval(self.request.headers.get('Authentication'))
            )
            token = auth_headers.get('token')
            if token:
                authenticated = token_exist_in_current(token)
                valid_previous_token = token_exist_in_previous(token)
                if authenticated:
                    return fn(self, *args, **kwargs)

                elif valid_previous_token:
                    msg = '{0} is a previous token'.format(token)
                    results[ApiResultKeys.INVALID_ID] = token
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ValidPreviousToken
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    self.set_status(
                        results[ApiResultKeys.HTTP_STATUS_CODE]
                    )
                    self.write(json.dumps(results, indent=4))

                else:
                    msg = '{0} is not a valid token'.format(token)
                    results[ApiResultKeys.INVALID_ID] = token
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewFailureCodes.InvalidToken
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    self.set_status(
                        results[ApiResultKeys.HTTP_STATUS_CODE]
                    )
                    self.write(json.dumps(results, indent=4))
            else:
                msg = 'Headers do not contain Authentication information'
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidHeaders
                )
                results[ApiResultKeys.MESSAGE] = msg
                self.set_status(
                    results[ApiResultKeys.HTTP_STATUS_CODE]
                )
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            msg = e
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.SomethingBroke
            )
            self.set_status(
                results[ApiResultKeys.HTTP_STATUS_CODE]
            )
            self.write(json.dumps(results, indent=4))

    return wrapper

def agent_results_message(fn):
    """Return the results in the vFense API standard"""
    def db_wrapper(*args, **kwargs):
        data = fn(*args, **kwargs)
        status_code = data.get(ApiResultKeys.VFENSE_STATUS_CODE, None)
        tornado_handler = args[0]
        agent_id = tornado_handler.get_agent_id()
        token = tornado_handler.get_token()
        method = tornado_handler.request.method
        uri = tornado_handler.request.uri
        status = None

        if status_code == AgentResultCodes.AgentAuthenticated:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).authenticated(**data)
            )

        elif status_code == AgentResultCodes.CheckInSucceeded:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).check_in(**data)
            )

        elif status_code == AgentResultCodes.TokenValidated:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).validated(**data)
            )

        elif status_code ==  AgentResultCodes.StartUpSucceeded:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).startup_succeeded(**data)
            )

        elif status_code == AgentResultCodes.NewAgentSucceeded:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).new_agent_succeeded(**data)
            )

        elif status_code == AgentFailureResultCodes.NewAgentFailed:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).new_agent_failed(**data)
            )

        elif status_code == AgentFailureResultCodes.StartupFailed:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).startup_failed(**data)
            )

        elif (status_code == AgentResultCodes.ResultsUpdated or
              status_code == AgentResultCodes.AgentUpdated):
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).agent_updated(**data)
            )

        elif status_code == AgentCodes.InformationRetrieved:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).information_retrieved(**data)
            )

        else:
            status = (
                AgentResults(
                    uri, method, token, agent_id
                ).something_broke(**data)
            )
        return status

    return wraps(fn)(db_wrapper)

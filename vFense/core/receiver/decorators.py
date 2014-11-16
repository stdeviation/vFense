import logging, logging.config
from ast import literal_eval
import json
from functools import wraps

from tornado.web import HTTPError

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.agent.status_codes import AgentCodes
from vFense.core.agent.manager import AgentManager
from vFense.core.agent._db_model import AgentKeys
from vFense.core.results import AgentApiResults, ApiResults
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.view._db import (
    token_exist_in_current, token_exist_in_previous
)
from vFense.core.view.status_codes import ViewCodes, ViewFailureCodes
from vFense.core.receiver.status_codes import (
    AgentResultCodes, AgentFailureResultCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_listener')


def authenticate_agent(fn):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        results = AgentApiResults()
        results.fill_in_defaults()
        results.uri = self.request.uri
        results.http_status_code = 403
        results.vfense_status_code = GenericCodes.AuthorizationDenied
        results.http_method = self.request.method
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
                        results.invalid_ids.append(token)
                        results.vfense_status_code = (
                            ViewCodes.ValidPreviousToken
                        )
                        results.message = msg
                        self.set_status(results.http_status_code)
                        self.write(
                            json.dumps(results.to_dict_non_null(), indent=4)
                        )

                    elif not authenticated and not valid_old_token:
                        msg = '{0} is not a valid token'.format(token)
                        results.invalid_ids.append(token)
                        results.vfense_status_code = (
                            ViewFailureCodes.InvalidToken
                        )
                        results.message = msg
                        self.set_status(results.http_status_code)
                        self.write(
                            json.dumps(results.to_dict_non_null(), indent=4)
                        )

                    elif not agent.get_attribute(AgentKeys.Enabled):
                        msg = '{0} is disabled'.format(agent_id)
                        results.agent_id = agent_id
                        results.vfense_status_code = AgentCodes.Disabled
                        results.message = msg
                        self.set_status(results.http_status_code)
                        self.write(
                            json.dumps(results.to_dict_non_null(), indent=4)
                        )

                else:
                    msg = '{0} not a valid agent id'.format(agent_id)
                    results.agent_id = agent_id
                    results.vfense_status_code = AgentCodes.AgentIdDoesNotExist
                    results.message = msg
                    self.set_status(results.http_status_code)
                    self.write(
                        json.dumps(results.to_dict_non_null(), indent=4)
                    )

            else:
                msg = 'Headers do not contain Authentication information'
                results.vfense_status_code = GenericFailureCodes.InvalidHeaders
                results.message = msg
                self.set_status(results.http_status_code)
                self.write(json.dumps(results.to_dict_non_null(), indent=4))

        except Exception as e:
            msg = e
            results.vfense_status_code = GenericCodes.SomethingBroke
            self.set_status(results.http_status_code)
            self.write(json.dumps(results.to_dict_non_null(), indent=4))

    return wrapper

def authenticate_token(fn):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        results = AgentApiResults()
        results.fill_in_defaults()
        results.uri = self.request.uri
        results.http_status_code = 403
        results.vfense_status_code = GenericCodes.AuthorizationDenied
        results.http_method = self.request.method
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
                    results.invalid_ids.append(token)
                    results.vfense_status_code = ViewCodes.ValidPreviousToken
                    results.message = msg
                    self.set_status(results.http_status_code)
                    self.write(
                        json.dumps(results.to_dict_non_null(), indent=4)
                    )

                else:
                    msg = '{0} is not a valid token'.format(token)
                    results.invalid_ids.append(token)
                    results.vfense_status_code = ViewFailureCodes.InvalidToken
                    results.message = msg
                    self.set_status(results.http_status_code)
                    self.write(
                        json.dumps(results.to_dict_non_null(), indent=4)
                    )
            else:
                msg = 'Headers do not contain Authentication information'
                results.vfense_status_code = GenericFailureCodes.InvalidHeaders
                results.message = msg
                self.set_status(results.http_status_code)
                self.write(
                    json.dumps(results.to_dict_non_null(), indent=4)
                )

        except Exception as e:
            msg = e
            results.message = msg
            print msg
            logger.exception(msg)
            results.vfense_status_code = GenericCodes.SomethingBroke
            self.set_status(results.http_status_code)
            self.write(json.dumps(results.to_dict_non_null(), indent=4))

    return wrapper

def agent_results_message(fn):
    """Return the results in the vFense API standard"""
    def db_wrapper(*args, **kwargs):
        data = fn(*args, **kwargs)
        tornado_handler = args[0]
        if isinstance(data, ApiResults):
            print data
            results = AgentApiResults(**data.to_dict_non_null())
            results.uri = tornado_handler.request.uri
            results.http_method = tornado_handler.request.method
            results.agent_id = tornado_handler.get_agent_id()
            results.token = tornado_handler.get_token()

            if results.vfense_status_code == AgentResultCodes.AgentAuthenticated:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        '{0} authenticated with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentResultCodes.CheckInSucceeded:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        '{0} checked in successfully with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentResultCodes.TokenValidated:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        '{0} token validated {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code ==  AgentResultCodes.StartUpSucceeded:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        'Startup succeeded for agent {0} with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentResultCodes.NewAgentSucceeded:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        'Newagent succeeded for agent {0} with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentFailureResultCodes.NewAgentFailed:
                results.http_status_code = 500
                if not results.message:
                    results.message = (
                        'Newagent failed for agent {0} with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentFailureResultCodes.StartupFailed:
                results.http_status_code = 500
                if not results.message:
                    results.message = (
                        'Startup failed for agent {0} with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif (results.vfense_status_code == AgentResultCodes.ResultsUpdated or
                  results.vfense_status_code == AgentResultCodes.AgentUpdated):
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        '{0} updated successfully with token {1}'
                        .format(results.agent_id, results.token)
                    )

            elif results.vfense_status_code == AgentCodes.InformationRetrieved:
                results.http_status_code = 200
                if not results.message:
                    results.message = (
                        '{0} retrieved data successfully with token {1}'
                        .format(results.agent_id, results.token)
                    )

            else:
                results.http_status_code = 500
                if not results.message:
                    results.message = (
                        'iSomething broke for agent {0} with token {1}'
                        .format(results.agent_id, results.token)
                    )
        else:
            results = AgentApiResults()
            results.fill_in_defaults()
            results.username = tornado_handler.get_current_user()
            results.uri = tornado_handler.request.uri
            results.http_method = tornado_handler.request.method
            results.agent_id = tornado_handler.get_agent_id()
            results.token = tornado_handler.get_token()
            results.http_status_code = 404
            if not results.message:
                results.message = '{0}: invalid instance'.format(type(data))

        return results

    return wraps(fn)(db_wrapper)

def agent_authenticated_request(method):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(403)

        return method(self, *args, **kwargs)

    return wrapper

def receiver_catch_it(fn):
    """wrap all receiver calls in a try catch exception"""
    def wrapper(*args, **kwargs):
        tornado_handler = args[0]
        try:
            results = fn(*args, **kwargs)
        except Exception as e:
            results = AgentApiResults()
            results.fill_in_defaults()
            results.generic_status_code = GenericCodes.SomethingBroke
            results.vfense_status_code = GenericCodes.SomethingBroke
            results.message = (
                'Something broke while calling {0}: {1}'
                .format(fn.__name__, e)
            )
            results.uri = tornado_handler.request.uri
            results.http_method = tornado_handler.request.method
            results.username = tornado_handler.get_current_user()
            results.http_status_code = 500
            results.agent_id = tornado_handler.get_agent_id()
            results.token = tornado_handler.get_token()
            results.errors.append(e)
            logger.exception(results.to_dict_non_null())
            tornado_handler.set_status(results.http_status_code)
            tornado_handler.set_header('Content-Type', 'application/json')
            tornado_handler.write(json.dumps(results.to_dict_non_null(), indent=4))

        return results

    return wraps(fn)(wrapper)

from vFense.result._constants import AgentApiResultKeys
from vFense.result.status_codes import (
    AgentResultCodes, AgentFailureResultCodes, GenericCodes, AgentCodes
)

class AgentResults(object):
    def __init__(self, uri, method, token, agent_id=None):
        self.uri = uri
        self.method = method
        self.agent_id = agent_id
        self.token = token

    def information_retrieved(self, **kwargs):
        msg = 'data retrieved for agent {0}'.format(self.agent_id)
        status_code = AgentCodes.InformationRetrieved
        data = kwargs.get(AgentApiResultKeys.DATA)
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
            }
        )


    def authenticated(self, **kwargs):
        msg = '{0} - agent was authenticated'.format(self.agent_id)
        status_code = AgentResultCodes.AgentAuthenticated
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
            }
        )

    def validated(self, **kwargs):
        msg = 'Token {0} validated'.format(self.token)
        status_code = AgentResultCodes.TokenValidated
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
            }
        )

    def new_agent_succeeded(self, **kwargs):
        msg = 'New agent succeeded'
        status_code = AgentResultCodes.NewAgentSucceeded
        agent_id = kwargs.get(AgentApiResultKeys.AGENT_ID)
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: agent_id,
            }
        )


    def new_agent_failed(self, **kwargs):
        msg = 'New agent operation failed'
        status_code = AgentFailureResultCodes.NewAgentFailed
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
            }
        )

    def startup_succeeded(self, **kwargs):
        msg = (
            'Start up operation for agent {0} succeeded'.format(self.agent_id)
        )
        status_code = AgentResultCodes.StartUpSucceeded
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
            }
        )

    def startup_failed(self, **kwargs):
        msg = 'Start up operation failed for agent {0}'.format(self.agent_id)
        status_code = AgentFailureResultCodes.StartupFailed
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
            }
        )

    def agent_updated(self, **kwargs):
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        unchanged_id = kwargs.get(AgentApiResultKeys.UNCHANGED_IDS, None)
        updated_id = kwargs.get(AgentApiResultKeys.UPDATED_IDS, None)
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        msg = (
            kwargs.get(
                AgentApiResultKeys.MESSAGE,
                'Agent {0} updated'.format(self.agent_id)
            )
        )
        status_code = (
            kwargs.get(
                AgentApiResultKeys.VFENSE_STATUS_CODE,
                AgentResultCodes.AgentUpdated
            )
        )
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.UPDATED_ID: updated_id,
                AgentApiResultKeys.UNCHANGED_ID: unchanged_id,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )

    def agent_failed_to_update(self, **kwargs):
        msg = 'Agent {0} update failed'.format(self.agent_id)
        status_code = AgentFailureResultCodes.ResultsFailedToUpdate
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.UNCHANGED_ID: self.agent_id,
            }
        )


    def invalid_id(self, **kwargs):
        invalid_id = kwargs.get(AgentApiResultKeys.INVALID_ID, '')
        msg = kwargs.get(AgentApiResultKeys.MESSAGE, '')
        status_code = (
            kwargs.get(
                AgentApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.InvalidId
            )
        )
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 404,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.INVALID_ID: invalid_id,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
            }
       )


    def something_broke(self, **kwargs):
        msg = kwargs.get(AgentApiResultKeys.MESSAGE, '')
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                AgentApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.SomethingBroke
            )
        )
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 500,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
            }
        )

    def object_exists(self, **kwargs):
        msg = kwargs.get(AgentApiResultKeys.MESSAGE, '')
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        unchanged_ids = kwargs.get(AgentApiResultKeys.UNCHANGED_IDS, [])
        status_code = (
            kwargs.get(
                AgentApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectExists
            )
        )
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
            }
        )

    def invalid_token(self, **kwargs):
        msg = 'Invalid Token {0}'.format(self.token)
        status_code = AgentFailureResultCodes.InvalidToken
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.INVALID_ID: self.token,
                AgentApiResultKeys.MESSAGE: msg,
            }
        )

    def check_in(self, **kwargs):
        msg = 'Checkin succeeded for agent {0}'.format(self.agent_id)
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        status_code = AgentResultCodes.CheckInSucceeded
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )

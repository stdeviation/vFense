from vFense.core.results import ApiResultKeys
from vFense.core.agent.status_codes import AgentCodes
from vFense.receiver.status_codes import (
    AgentResultCodes, AgentFailureResultCodes
)

class AgentApiResultKeys(ApiResultKeys):
    OPERATIONS = 'operations'
    OPERATION = 'operation'
    NEW_TOKEN_ID = 'new_token_id'
    AGENT_ID = 'agent_id'
    UPDATED_ID = 'updated_id'
    UNCHANGED_ID = 'unchanged_id'

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
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )


    def authenticated(self, **kwargs):
        msg = '{0} - agent was authenticated'.format(self.agent_id)
        status_code = AgentResultCodes.AgentAuthenticated
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
            }
        )

    def validated(self, **kwargs):
        msg = 'Token {0} validated'.format(self.token)
        status_code = AgentResultCodes.TokenValidated
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
            }
        )

    def new_agent_succeeded(self, **kwargs):
        msg = 'New agent succeeded'
        status_code = AgentResultCodes.NewAgentSucceeded
        agent_id = kwargs.get(AgentApiResultKeys.AGENT_ID)
        generated_ids = [agent_id]
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        data = kwargs.get(AgentApiResultKeys.DATA)
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.AGENT_ID: agent_id,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.GENERATED_IDS: generated_ids,
                AgentApiResultKeys.DATA: data,
            }
        )


    def new_agent_failed(self, **kwargs):
        msg = 'New agent operation failed'
        status_code = AgentFailureResultCodes.NewAgentFailed
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
            }
        )

    def startup_succeeded(self, **kwargs):
        msg = (
            'Start up operation for agent {0} succeeded'.format(self.agent_id)
        )
        status_code = AgentResultCodes.StartUpSucceeded
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.AGENT_ID: self.agent_id,
                AgentApiResultKeys.DATA: [],
            }
        )

    def startup_failed(self, **kwargs):
        msg = 'Start up operation failed for agent {0}'.format(self.agent_id)
        status_code = AgentFailureResultCodes.StartupFailed
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
            }
        )

    def agent_updated(self, **kwargs):
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        unchanged_id = kwargs.get(AgentApiResultKeys.UNCHANGED_IDS, None)
        updated_id = kwargs.get(AgentApiResultKeys.UPDATED_IDS, None)
        generated_ids = kwargs.get(AgentApiResultKeys.GENERATED_IDS, [])
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
                AgentApiResultKeys.GENERATED_IDS: generated_ids,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )

    def agent_failed_to_update(self, **kwargs):
        msg = 'Agent {0} update failed'.format(self.agent_id)
        status_code = AgentFailureResultCodes.ResultsFailedToUpdate
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 409,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.UNCHANGED_ID: self.agent_id,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
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
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 404,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.INVALID_ID: invalid_id,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.DATA: data,
                AgentApiResultKeys.OPERATIONS: operations,
            }
       )


    def something_broke(self, **kwargs):
        msg = kwargs.get(AgentApiResultKeys.MESSAGE, '')
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
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
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )

    def object_exists(self, **kwargs):
        msg = kwargs.get(AgentApiResultKeys.MESSAGE, '')
        data = kwargs.get(AgentApiResultKeys.DATA, [])
        unchanged_ids = kwargs.get(AgentApiResultKeys.UNCHANGED_IDS, [])
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
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
                AgentApiResultKeys.OPERATIONS: operations,
            }
        )

    def invalid_token(self, **kwargs):
        msg = 'Invalid Token {0}'.format(self.token)
        status_code = AgentFailureResultCodes.InvalidToken
        operations = kwargs.get(AgentApiResultKeys.OPERATIONS, [])
        return(
            {
                AgentApiResultKeys.HTTP_STATUS_CODE: 200,
                AgentApiResultKeys.VFENSE_STATUS_CODE: status_code,
                AgentApiResultKeys.URI: self.uri,
                AgentApiResultKeys.HTTP_METHOD: self.method,
                AgentApiResultKeys.INVALID_ID: self.token,
                AgentApiResultKeys.MESSAGE: msg,
                AgentApiResultKeys.OPERATIONS: operations,
                AgentApiResultKeys.DATA: [],
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
                AgentApiResultKeys.DATA: [],
            }
        )

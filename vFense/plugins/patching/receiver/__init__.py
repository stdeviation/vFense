from vFense import Base
from vFense.plugins.patching.receiver._constants import (
    RefreshAppsResultsKeys, RefreshAppsResultsDefaults
)
class RefreshAppsResults(Base):
    def __init__(self, agent_id=None, operation_id=None, error=None,
                 success=None, apps_data=None, status_code=None, **kwargs
                 ):
        super(RefreshAppsResults, self).__init__(**kwargs)
        self.agent_id = agent_id
        self.operation_id = operation_id
        self.error = error
        self.success = success
        self.apps_data = apps_data
        self.status_code = status_code

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.error:
            self.error = RefreshAppsResultsDefaults.error()

        if not self.success:
            self.success = RefreshAppsResultsDefaults.success()

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            RefreshAppsResultsKeys.AgentId: self.agent_id,
            RefreshAppsResultsKeys.OperationId: self.operation_id,
            RefreshAppsResultsKeys.Error: self.error,
            RefreshAppsResultsKeys.Success: self.success,
            RefreshAppsResultsKeys.AppsData: self.apps_data,
            RefreshAppsResultsKeys.StatusCode: self.status_code
        }




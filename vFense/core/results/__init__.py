from vFense import Base
from vFense.core.results._constants import ApiResultDefaults, ApiResultKeys


class ApiResults(Base):
    """Used to represent an instance of api results."""

    def __init__(self, updated_ids=None, invalid_ids=None, unchanged_ids=None,
                 deleted_ids=None, generic_status_code=None, data=None,
                 vfense_status_code=None, db_status_code=None,
                 message=None, errors=None, agent_id=None, tag_id=None,
                 generated_ids=None, count=0, **kwargs
                 ):
        """
        Kwargs:
        """
        super(ApiResults, self).__init__(**kwargs)
        self.updated_ids = updated_ids
        self.invalid_ids = invalid_ids
        self.unchanged_ids = unchanged_ids
        self.deleted_ids = deleted_ids
        self.db_status_code = db_status_code
        self.generic_status_code = generic_status_code
        self.vfense_status_code = vfense_status_code
        self.message = message
        self.data = data
        self.generated_ids = generated_ids
        self.errors = errors
        self.count = count

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.updated_ids:
            self.updated_ids = ApiResultDefaults.updated_ids()

        if not self.invalid_ids:
            self.invalid_ids = ApiResultDefaults.invalid_ids()

        if not self.unchanged_ids:
            self.unchanged_ids = ApiResultDefaults.unchanged_ids()

        if not self.deleted_ids:
            self.deleted_ids = ApiResultDefaults.deleted_ids()

        if not self.data:
            self.data = ApiResultDefaults.data()

        if not self.count:
            self.count = 0

        if not self.generated_ids:
            self.generated_ids = ApiResultDefaults.generated_ids()

        if not self.errors:
            self.errors = ApiResultDefaults().errors()


    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            ApiResultKeys.UPDATED_IDS: self.updated_ids,
            ApiResultKeys.UNCHANGED_IDS: self.unchanged_ids,
            ApiResultKeys.DELETED_IDS: self.deleted_ids,
            ApiResultKeys.INVALID_IDS: self.invalid_ids,
            ApiResultKeys.GENERATED_IDS: self.generated_ids,
            ApiResultKeys.GENERIC_STATUS_CODE: self.generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: self.vfense_status_code,
            ApiResultKeys.DATA: self.data,
            ApiResultKeys.MESSAGE: self.message,
            ApiResultKeys.ERRORS: self.errors,
            ApiResultKeys.COUNT: self.count,
        }


class ExternalApiResults(ApiResults):
    def __init__(self, uri=None, http_method=None, username=None,
                 count=0, http_status_code=None, **kwargs):
        super(ExternalApiResults, self).__init__(**kwargs)
        self.uri = uri
        self.http_method = http_method
        self.username = username
        self.count = count
        self.http_status_code = http_status_code

    def to_dict(self):
        data = {
            ApiResultKeys.COUNT: self.count,
            ApiResultKeys.HTTP_STATUS_CODE: self.http_status_code,
            ApiResultKeys.USERNAME: self.username,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.http_method,
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data


class AgentApiResults(ApiResults):
    def __init__(self, uri=None, http_method=None, agent_id=None, token=None,
                 username=None, operations=None, http_status_code=None,
                 **kwargs):
        super(AgentApiResults, self).__init__(**kwargs)
        self.uri = uri
        self.http_method = http_method
        self.agent_id = agent_id
        self.operations = operations
        self.token = token
        self.username = username

    def to_dict(self):
        data = {
            ApiResultKeys.OPERATIONS: self.operations,
            ApiResultKeys.HTTP_STATUS_CODE: self.http_status_code,
            ApiResultKeys.USERNAME: self.username,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.http_method,
            ApiResultKeys.AGENT_ID: self.agent_id,
            ApiResultKeys.TOKEN: self.token,
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

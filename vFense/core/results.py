from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes
)

from vFense.core._constants import ApiResultDefaults

class ApiResultKeys():
    URI = 'uri'
    HTTP_METHOD = 'http_method'
    USERNAME = 'user_name'
    COUNT = 'count'
    HTTP_STATUS_CODE = 'http_status'
    GENERIC_STATUS_CODE = 'generic_status_code'
    VFENSE_STATUS_CODE = 'vfense_status_code'
    ERRORS = 'errors'
    DB_STATUS_CODE = 'db_status_code'
    MESSAGE = 'message'
    DATA = 'data'
    ELAPSED_SECONDS = 'elapsed_seconds'
    GENERATED_IDS = 'generated_ids'
    UNCHANGED_IDS = 'unchanged_ids'
    SKIPPED_IDS = 'skipped_ids'
    MODIFIED_IDS = 'modified_ids'
    UPDATED_IDS = 'updated_ids'
    DELETED_IDS = 'deleted_ids'
    INVALID_IDS = 'invalid_ids'
    INVALID_ID = 'invalid_id'
    OPERATIONS = 'operations'
    INVALID_DATA = 'invalid_data'
    USERNAME_IDS = 'user_name'
    NEW_TOKEN_ID = 'new_token_id'
    AGENT_ID = 'agent_id'


class ApiResults(object):
    """Used to represent an instance of api results."""

    def __init__(self, updated_ids=None, invalid_ids=None, unchanged_ids=None,
                 deleted_ids=None, generic_status_code=None, data=None,
                 vfense_status_code=None, db_status_code=None,
                 message=None, errors=None, agent_id=None, tag_id=None,
                 generated_ids=None
                 ):
        """
        Kwargs:
        """
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

        if not self.operations:
            self.operations = ApiResultDefaults.operations()

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
        }


class ExternalApiResults(ApiResults):
    def __init__(self, uri=None, http_method=None, username=None,
                 count=0, http_status_code=None, **kwargs):
        super(ExternalApiResults, self).__init__(**kwargs)
        self.uri = uri
        self.http_method = http_method
        self.username = username
        self.count = count

    def to_dict(self):
        data = {
            ApiResultKeys.COUNT: self.count,
            ApiResultKeys.HTTP_STATUS_CODE: self.http_status_code,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.http_method,
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data


class AgentApiResults(ApiResults):
    def __init__(self, uri=None, http_method=None, agent_id=None,
                 operations=None, **kwargs):
        super(AgentApiResults, self).__init__(**kwargs)
        self.uri = uri
        self.http_method = http_method
        self.agent_id = agent_id
        self.operations = operations

    def to_dict(self):
        data = {
            ApiResultKeys.OPERATIONS: self.operations,
            ApiResultKeys.HTTP_STATUS_CODE: self.http_status_code,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.http_method,
            ApiResultKeys.AGENT_ID: self.agent_id,
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data



class Results(object):
    def __init__(self, username, uri, method):
        self.uri = uri
        self.method = method
        self.username = username

    def data_retrieved(self, **kwargs):
        msg = (
            kwargs.get(
                ApiResultKeys.MESSAGE,
                '%s - data was retrieved' % (self.username)
            )
        )
        data = kwargs.get(ApiResultKeys.DATA, [])
        count = kwargs.get(ApiResultKeys.COUNT, 0)
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.InformationRetrieved
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
                ApiResultKeys.COUNT: count
            }
        )

    def objects_created(self, **kwargs):
        generated_ids = kwargs.get(ApiResultKeys.GENERATED_IDS, [])
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectCreated
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.GENERATED_IDS: generated_ids,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def objects_failed_to_create(self, **kwargs):
        generated_ids = kwargs.get(ApiResultKeys.GENERATED_IDS, [])
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericFailureCodes.FailedToCreateObject
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 409,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.GENERATED_IDS: generated_ids,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def objects_updated(self, **kwargs):
        updated_ids = kwargs.get(ApiResultKeys.UPDATED_IDS, [])
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectUpdated
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.UPDATED_IDS: updated_ids,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def objects_failed_to_update(self, **kwargs):
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericFailureCodes.FailedToUpdateObject
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 409,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def objects_deleted(self, **kwargs):
        deleted_ids = kwargs.get(ApiResultKeys.DELETED_IDS, [])
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectDeleted
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.DELETED_IDS: deleted_ids,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
       )


    def objects_failed_to_delete(self, **kwargs):
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericFailureCodes.FailedToDeleteObject
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 409,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def invalid_id(self, **kwargs):
        invalid_id = kwargs.get(ApiResultKeys.INVALID_ID, '')
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.InvalidId
            )
        )
        data = kwargs.get(ApiResultKeys.DATA, [])
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 404,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.INVALID_ID: invalid_id,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
       )


    def does_not_exist(self, **kwargs):
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.DoesNotExist
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 409,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
            }
        )


    def objects_unchanged(self, **kwargs):
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectUnchanged
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )


    def something_broke(self, **kwargs):
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.SomethingBroke
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 500,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )

    def object_exists(self, **kwargs):
        msg = kwargs.get(ApiResultKeys.MESSAGE, '')
        data = kwargs.get(ApiResultKeys.DATA, [])
        unchanged_ids = kwargs.get(ApiResultKeys.UNCHANGED_IDS, [])
        status_code = (
            kwargs.get(
                ApiResultKeys.VFENSE_STATUS_CODE,
                GenericCodes.ObjectExists
            )
        )
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: status_code,
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.UNCHANGED_IDS: unchanged_ids,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )

    def permission_denied(self):
        msg = 'Permission denied for user {0}'.format(self.username)

        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 403,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.PermissionDenied
                ),
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: [],
            }
        )

    def invalid_permission(self, **kwargs):
        msg = 'Invalid permission for user {0}'.format(self.username)
        data = kwargs.get(ApiResultKeys.DATA, [])
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 403,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.InvalidPermission
                ),
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )

    def incorrect_arguments(self, **kwargs):
        msg = 'Incorrect arguments'
        data = kwargs.get(ApiResultKeys.DATA, [])
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.IncorrectArguments
                ),
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: data,
            }
        )

    def auth_granted(self, **kwargs):
        msg = 'Authorization granted'
        return(
            {
                ApiResultKeys.HTTP_STATUS_CODE: 200,
                ApiResultKeys.VFENSE_STATUS_CODE: (
                    GenericCodes.AuthorizationGranted
                ),
                ApiResultKeys.URI: self.uri,
                ApiResultKeys.HTTP_METHOD: self.method,
                ApiResultKeys.MESSAGE: msg,
                ApiResultKeys.DATA: [],
            }
        )

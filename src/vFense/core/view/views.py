import logging
import re

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import CPUThrottleValues, DefaultStringLength
from vFense.core._db import retrieve_object
from vFense.core.view._db_model import *
from vFense.core.view._constants import DefaultViews
from vFense.core.user._db_model import UserCollections
from vFense.core.user._constants import DefaultUsers
from vFense.core.view._db import insert_view, fetch_view, \
    insert_user_per_view, delete_user_in_views , delete_view, \
    users_exists_in_view, update_view, fetch_users_for_view, \
    fetch_properties_for_all_views, fetch_properties_for_view, \
    users_exists_in_views, delete_views, delete_users_in_view

from vFense.core.group._db  import delete_groups_from_view
from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *
from vFense.errorz._constants import ApiResultKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def get_view(view_name, keys_to_pluck=None):
    """Retrieve view information.
    Args:
        view_name (str):  Name of the view.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage:
        >>> from vFense.view.views get_view
        >>> view_name = 'default'
        >>> get_view(view_name)

    Return:
        Dictionary of view properties.
        {
            u'cpu_throttle': u'normal',
            u'package_download_url_base': u'http: //10.0.0.21/packages/',
            u'operation_ttl': 10,
            u'net_throttle': 0,
            u'view_name': u'default'
        }
    """
    view_data = {}
    if keys_to_pluck:
        view_data = fetch_view(view_name, keys_to_pluck)
    else:
        view_data = fetch_view(view_name)

    return(view_data)


@time_it
def get_view_property(view_name, view_property):
    """Retrieve view property.
    Args:
        view_name (str):  Name of the view.

    Kwargs:
        view_property (str): Property you want to retrieve.

    Basic Usage:
        >>> from vFense.view.views get_view_property
        >>> view_name = 'default'
        >>> view_property = 'operation_ttl'
        >>> get_view(view_name)

    Return:
        String
    """
    view_data = fetch_view(view_name)
    view_key = None
    if view_data:
        view_key = view_data.get(view_property)

    return(view_key)


@time_it
def get_views(match=None, keys_to_pluck=None):
    """Retrieve all views or just views based on regular expressions
    Kwargs:
        match (str): Regular expression of the view name
            you are searching for.
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Returns:
        Returns a List of views

    Basic Usage::
        >>> from vFense.view.views import get_views
        >>> get_views()

    Return:
        List of dictionaries of view properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'TopPatch'
            }
        ]
    """
    view_data = {}
    if match and keys_to_pluck:
        view_data = fetch_views(match, keys_to_pluck)

    elif match and not keys_to_pluck:
        view_data = fetch_views(match)

    elif not match and keys_to_pluck:
        view_data = fetch_views(keys_to_pluck)

    elif not match and not keys_to_pluck:
        view_data = fetch_views()

    return(view_data)


@time_it
def get_properties_for_view(view_name):
    """Retrieve a view and all its properties
    Args:
        view_name (str): Name of the view

    Returns:
        Returns a Dictionary of views

    Basic Usage::
        >>> from vFense.view.view import get_properties_for_view
        >>> get_properties_for_view(view_name)

    Return:
        Dictionary of view properties.
    """
    data = fetch_properties_for_view(view_name)
    return(data)


@time_it
def get_properties_for_all_views(username=None):
    """Retrieve all views or retrieve all views that user has
        access to.
    Kwargs:
        user_name (str): Name of the username, w

    Returns:
        Returns a List of views

    Basic Usage::
        >>> from vFense.view.view import get_properties_for_all_views
        >>> fetch_properties_for_all_views()

    Return:
        List of view properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'TopPatch'
            }
        ]
    """
    data = fetch_properties_for_all_views(username)
    return(data)


@time_it
def validate_view_names(view_names):
    """Validate a list if view names.
    Args:
        view_names (list): List of view names.

    Basic Usage:
        >>> from vFense.view.views import validate_view_names
        >>> view_names = ['default', 'TOpPatch']
        >>> validate_view_names(view_names)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['default'], ['TOpPatch'])
    """
    validated = True
    invalid_names = []
    valid_names = []
    if isinstance(view_names, list):
        for view_name in view_names:
            if fetch_view(view_name):
                valid_names.append(view_name)
            else:
                invalid_names.append(view_name)
                validated = False

    return(validated, valid_names, invalid_names)


@time_it
@results_message
def add_user_to_views(
    username, view_names,
    user_name=None, uri=None, method=None
    ):
    """Add a multiple views to a user
    Args:
        username (str):  Name of the user already in vFense.
        view_names (list): List of view names,
            this user will be added to.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view.view import add_user_to_views
        >>> username = 'admin'
        >>> view_names = ['default', 'TopPatch', 'vFense']
        >>> add_user_to_views(username, view_names)

    Returns:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1017,
            'http_method': None,
            'http_status': 200,
            'message': "None - add_user_to_views - view names existed 'default', 'TopPatch', 'vFense' unchanged",
            'data': []

        }
    """
    if isinstance(view_names, str):
        view_names = view_names.split(',')

    views_are_valid = validate_view_names(view_names)
    results = None
    user_exist = retrieve_object(username, UserCollections.Users)
    data_list = []
    status = add_user_to_views.func_name + ' - '
    msg = ''
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    generated_ids = []
    if views_are_valid[0]:
        data_list = []
        for view_name in view_names:
            if not users_exists_in_view(username, view_name):
                data_to_add = (
                    {
                        ViewPerUserKeys.ViewName: view_name,
                        ViewPerUserKeys.UserName: username,
                    }
                )
                data_list.append(data_to_add)

        if user_exist and data_list:
            status_code, object_count, error, generated_ids = (
                insert_user_per_view(data_list)
            )
            if status_code == DbCodes.Inserted:
                msg = (
                    'user %s added to %s' % (
                        username, ' and '.join(view_names)
                    )
                )
                generic_status_code = GenericCodes.ObjectCreated
                vfense_status_code = ViewCodes.ViewsAddedToUser

        elif user_exist and not data_list:
            status_code = DbCodes.Unchanged
            msg = 'view names existed for user %s' % (username)
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = ViewFailureCodes.UsersExistForView

        elif not user_exist:
            status_code = DbCodes.Errors
            msg = 'User name is invalid: %s' % (username)
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExist

    elif not views_are_valid[0]:
        status_code = DbCodes.Errors
        msg = (
            'View names are invalid: %s' % (
                ' and '.join(views_are_valid[2])
            )
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = ViewFailureCodes.InvalidViewName

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.GENERATED_IDS: generated_ids,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


#def create_view(
#    view_name, username=None,
#    http_application_url_location=None,
#    net_throttle=0, cpu_throttle='normal',
#    server_queue_ttl=10, agent_queue_ttl=10,
#    init=False, user_name=None, uri=None, method=None
#    ):
@time_it
@results_message
def create_view(
        view, username=None, init=None,
        user_name=None, uri=None, method=None
    ):
    """Create a new view inside of vFense

    Args:
        view (View): A view instance filled out with the
            appropriate fields.

    Kwargs:
        username (str): Name of the user that you are adding to this view.
            Default=None
            If init is set to True, then it can stay as None
            else, then a valid user must be passed
        init (boolean): Create the view, without adding a user into it.
            Default=False
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view._db_model import View
        >>> from vFense.core.view.views import create_view
        >>> view = View('NewView', package_download_url='https://10.0.0.16/packages/')
        >>> username = 'api_user'
        >>> create_view(view, api_user)

    Return:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1010,
            'http_method': None,
            'http_status': 200,
            'message': 'api_user - view vFense was created',
            'data': {
                'cpu_throttle': 'normal',
                'package_download_url_base': 'https: //10.0.0.21/packages/',
                'server_queue_ttl': 10,
                'agent_queue_ttl': 10,
                'net_throttle': 0,
                'view_name': 'vFense'
            }
        }
    """
    view_exist = fetch_view(view.name)

    status = create_view.func_name + ' - '
    msg = ''
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    generated_ids = []

    invalid_fields = view.get_invalid_fields()

    if invalid_fields:
        # TODO: Inform about more than just the first invalid field
        invalid_field = invalid_fields[0]

        status_code = DbCodes.Errors
        generic_status_code = GenericCodes.InvalidId

        if invalid_field.get(ViewKeys.ViewName):
            msg = (
                'view name is not within the 36 character range '
                'or contains unsupported characters :%s' %
                (invalid_field.get(ViewKeys.ViewName))
            )
            vfense_status_code = ViewFailureCodes.InvalidViewName

        elif invalid_field.get(ViewKeys.NetThrottle):
            msg = (
                'network throttle was not given a valid integer :%s' %
                (invalid_field.get(ViewKeys.NetThrottle))
            )
            vfense_status_code = ViewFailureCodes.InvalidNetworkThrottle

        elif invalid_field.get(ViewKeys.CpuThrottle):
            msg = (
                'cpu throttle was not given a valid value :%s' %
                (invalid_field.get(ViewKeys.CpuThrottle))
            )
            vfense_status_code = ViewFailureCodes.InvalidCpuThrottle

        elif invalid_field.get(ViewKeys.ServerQueueTTL):
            msg = (
                'server queue ttl was not given a valid value :%s' %
                (invalid_field.get(ViewKeys.ServerQueueTTL))
            )
            vfense_status_code = ViewFailureCodes.InvalidOperationTTL

        elif invalid_field.get(ViewKeys.AgentQueueTTL):
            msg = (
                'agent queue ttl was not given a valid value :%s' %
                (invalid_field.get(ViewKeys.AgentQueueTTL))
            )
            vfense_status_code = ViewFailureCodes.InvalidOperationTTL

        # TODO: handle invalid base package url string
        #elif invalid_field.get(ViewKeys.PackageUrl):

    elif not view_exist:
        # Fill in any empty fields
        view.fill_in_defaults()

        if not view.package_download_url:
            view.package_download_url = (
                fetch_view(
                    DefaultViews.DEFAULT,
                    [ViewKeys.PackageUrl]
                ).get(ViewKeys.PackageUrl)
            )

        object_status, _, _, generated_ids = (
            insert_view(view.to_dict())
        )

        if object_status == DbCodes.Inserted:
            generated_ids.append(view.name)
            msg = 'view %s created - ' % (view.name)
            generic_status_code = GenericCodes.ObjectCreated
            vfense_status_code = ViewCodes.ViewCreated

        if object_status == DbCodes.Inserted and not init and username:
            add_user_to_views(
                username, [view.name], user_name, uri, method
            )

            if username != DefaultUsers.ADMIN:
                add_user_to_views(
                    DefaultUsers.ADMIN, [view.name], user_name, uri, method
                )

        #The admin user should be part of every group
        elif object_status == DbCodes.Inserted and username != DefaultUsers.ADMIN:
            admin_exist = (
                retrieve_object(
                    DefaultUsers.ADMIN, UserCollections.Users
                )
            )

            if admin_exist:
                add_user_to_views(
                    DefaultUsers.ADMIN, [view.name], user_name, uri, method
                )

    elif view_exist:
        status_code = DbCodes.Unchanged
        msg = 'view name %s already exists' % (view.name)
        generic_status_code = GenericCodes.ObjectExists
        vfense_status_code = ViewFailureCodes.ViewExists

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [view.to_dict()],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def edit_view(view, **kwargs):
    """ Edit the properties of a view.

    Args:
        view (View): A view instance filled with values
            that should be changed.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view.views edit_view
        >>> view_name = 'agent_api'
        >>> edit_view(view_name, server_queue_ttl=5)

    Returns:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - view modified - default was updated',
            'data': {
                'server_queue_ttl': 5
            }
        }
    """

    if not kwargs.get(ApiResultKeys.USERNAME):
        user_name = None
    else:
        user_name = kwargs.pop(ApiResultKeys.USERNAME)

    if not kwargs.get(ApiResultKeys.URI):
        uri = None
    else:
        uri = kwargs.pop(ApiResultKeys.URI)

    if not kwargs.get(ApiResultKeys.HTTP_METHOD):
        method = None
    else:
        method = kwargs.pop(ApiResultKeys.HTTP_METHOD)

    status = edit_view.func_name + ' - '
    update_data = view.to_dict_non_null()

    msg = ''
    generic_status_code = None
    vfense_status_code = None
    try:
        invalid_data = view.get_invalid_fields()

        if invalid_data:
            msg = (
                'data was invalid for view %s: %s- ' %
                (view.name, invalid_data)
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectUnchanged
            vfense_status_code = ViewCodes.ViewUnchanged

        else:
            status_code, _, _, _ = update_view(
                view.name, update_data
            )

            if status_code == DbCodes.Replaced:
                msg = 'view %s updated - ' % (view.name)
                generic_status_code = GenericCodes.ObjectUpdated
                vfense_status_code = ViewCodes.ViewUpdated

            elif status_code == DbCodes.Unchanged:
                msg = 'view %s unchanged - ' % (view.name)
                generic_status_code = GenericCodes.ObjectUnchanged
                vfense_status_code = ViewCodes.ViewUnchanged

            elif status_code == DbCodes.Skipped:
                msg = 'view %s does not exist - ' % (view.name)
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = ViewFailureCodes.InvalidViewName

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to modify view %s: %s' % (view.name, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = ViewFailureCodes.FailedToRemoveView

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [update_data],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def remove_views_from_user(
    username, view_names=None,
    user_name=None, uri=None, method=None
    ):
    """Remove a view from a user
    Args:
        username (str): Username of the user, you are
            removing the view from.

    Kwargs:
        view_names (list): List of view_names,
            you want to remove from this user
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.view.views remove_views_from_user
        >>> username = 'agent_api'
        >>> remove_views_from_user(username)

    Return:
        Dictionary of the status of the operation.
    {
        'rv_status_code': 1004,
        'message': 'None - remove_views_from_user - removed views from user alien: TopPatch and vFense does not exist',
        'http_method': None,
        'uri': None,
        'http_status': 409
    }
    """
    status = remove_views_from_user.func_name + ' - '
    try:
        status_code, count, errors, generated_ids = (
            delete_user_in_views(username, view_names)
        )
        if status_code == DbCodes.Deleted:
            msg = 'removed views from user %s' % (username)
            generic_status_code = GenericCodes.ObjectDeleted
            vfense_status_code = ViewCodes.ViewsRemovedFromUser

        elif status_code == DbCodes.Skipped:
            msg = 'invalid view name or invalid username'
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = ViewFailureCodes.InvalidViewName

        elif status_code == DbCodes.DoesNotExist:
            msg = 'view name or username does not exist'
            generic_status_code = GenericCodes.DoesNotExist
            vfense_status_code = ViewFailureCodes.UsersDoNotExistForView

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = (
            'Failed to remove views from user %s: %s' %
            (username, str(e))
        )
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = ViewFailureCodes.FailedToRemoveView

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_view(view_name, user_name=None, uri=None, method=None):
    """ Remove a view from vFense
    Args:
        view_name: Name of the view you are removing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view.views remove_view
        >>> view_name = 'nyc'
        >>> remove_view(view_name)

    Return:
        Dictionary of the status of the operation.
        {
            'rv_status_code': 1012,
            'message': 'None - remove_view - vFense was deleted',
            'http_method': None,
            'uri': None,
            'http_status': 200

        }
    """
    status = remove_view.func_name + ' - '
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    views_deleted = []
    try:
        view_exist = fetch_view(view_name)
        default_in_list = DefaultViews.DEFAULT == view_name

        if view_exist and not default_in_list:
            status_code, count, errors, generated_ids = (
                delete_view(view_name)
            )

            if status_code == DbCodes.Deleted:
                msg = 'view %s removed' % view_name
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = ViewCodes.ViewDeleted
                views_deleted.append(view_name)
                delete_groups_from_view(view_name)
                users = (
                    fetch_users_for_view(
                        view_name, ViewPerUserKeys.UserName
                    )
                )
                if users:
                    users = (
                        map(
                            lambda user:
                            user[ViewPerUserKeys.UserName], users
                        )
                    )
                    delete_users_in_view(users, view_name)


        elif default_in_list:
            msg = 'Can not delete the default view'
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = ViewFailureCodes.CantDeleteDefaultView

        else:
            msg = 'view %s does not exist' % (view_name)
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = ViewFailureCodes.InvalidViewName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: views_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove view %s: %s' % (view_name, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = ViewFailureCodes.FailedToRemoveView

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: views_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_views(view_names, user_name=None, uri=None, method=None):
    """ Remove a view from vFense
    Args:
        view_names: Name of the views you are removing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view.views remove_views
        >>> view_names = ['nyc', 'foo']
        >>> remove_views(view_names)

    Return:
        Dictionary of the status of the operation.
        {
            'rv_status_code': 1012,
            'message': 'None - remove_view - vFense was deleted',
            'http_method': None,
            'uri': None,
            'http_status': 200

        }
    """
    status = remove_view.func_name + ' - '
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    views_deleted = []
    try:
        views_are_valid = validate_view_names(view_names)
        users_exist = users_exists_in_views(view_names)
        default_in_list = DefaultViews.DEFAULT in view_names
        if views_are_valid[0] and not users_exist[0] and not default_in_list:
            status_code, count, errors, generated_ids = (
                delete_views(view_names)
            )
            if status_code == DbCodes.Deleted:
                msg = 'views %s removed' % view_names
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = ViewCodes.ViewDeleted
                views_deleted = view_names
                ### Delete all the groups that belong to these views
                ### And remove the users from these views as well.
                for view_name in view_names:
                    delete_groups_from_view(view_name)
                    users = (
                        fetch_users_for_view(
                            view_name, ViewPerUserKeys.UserName
                        )
                    )
                    if users:
                        users = (
                            map(
                                lambda user:
                                user[ViewPerUserKeys.UserName], users
                            )
                        )
                        delete_users_in_view(users, view_name)


        elif users_exist[0] and not default_in_list:
            msg = (
                'users still exist for view %s' %
                (' and '.join(users_exist[1]))
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = ViewFailureCodes.UsersExistForView

        elif default_in_list:
            msg = 'Can not delete the default view'
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = ViewFailureCodes.CantDeleteDefaultView

        else:
            msg = (
                'view %s does not exist' %
                (' and '.join(views_are_valid[2]))
            )
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = ViewFailureCodes.InvalidViewName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.DELETED_IDS: views_deleted,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove view %s: %s' % (view_names, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = ViewFailureCodes.FailedToRemoveView

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: views_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)

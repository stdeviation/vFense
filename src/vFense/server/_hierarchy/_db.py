# This is the backend for hierarchy package. _db should not be used directly.
# Safer to use hierarchy and its User, Group, View class.

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from copy import deepcopy
from vFense.db.client import *

from vFense.groups import *
from vFense.users import *
from vFense.views import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@db_create_close
def _db_document_exist(_id=None, collection_name=None, conn=None):
    """Checks if a document exist for given id.

     Args:

        _id: Used to check for a document.

        collection_name: Name of collection to be searched.

    Returns:

        True if a document exist, False otherwise.
    """

    if not _id and not collection_name:

        return False

    doc = r.table(collection_name).get(_id).run(conn)

    if doc:

        return True

    return False


class _RawModels():
    """Wrapper class to help with converting models to a basic raw dict.
    """

    @staticmethod
    def _db_raw_group(group):
        """Creates a raw dict with Group properties.

        Args:

            group: A Group instance.

        Returns:

            A dict with group properties.
        """

        _raw = {}

        if not group:

            return _raw

        _raw[GroupKey.Name] = group.name
        _raw[GroupKey.Id] = group.id
        _raw[GroupKey.Permissions] = group.get_permissions()
        _raw[GroupKey.View] = group.get_view(raw=True)
        _raw[GroupKey.Users] = group.get_users(raw=True)

        return _raw

    @staticmethod
    def _db_raw_user(user):
        """Creates a raw dict with User properties.

        Args:

            user: A User instance.

        Returns:

            A dict with user properties.
        """

        _raw = {}

        if not user:

            return _raw

        _raw[UserKey.Name] = user.name
        _raw[UserKey.Id] = user.id
        _raw[UserKey.FullName] = user.full_name
        _raw[UserKey.Email] = user.email
        _raw[UserKey.Password] = user.hash_password
        _raw[UserKey.Enabled] = user.enabled

        _raw[UserKey.CurrentView] = user.get_current_view(raw=True)
        _raw[UserKey.DefaultView] = user.get_default_view(raw=True)

        _raw[UserKey.Views] = user.get_views(raw=True)
        _raw[UserKey.Groups] = user.get_groups(raw=True)

        return _raw

    @staticmethod
    def _db_raw_view(view):
        """Creates a raw dict with View properties.

        Args:

            view: A View instance.

        Returns:

            A dict with view properties.
        """

        _raw = {}

        if not view:

            return _raw

        _raw[ViewKey.Name] = view.name
        _raw[ViewKey.Id] = view.id
        _raw[ViewKey.NetThrottle] = view.net_throttle

        _raw[ViewKey.Groups] = view.get_groups(raw=True)
        _raw[ViewKey.Users] = view.get_users(raw=True)

        return _raw


@db_create_close
def get_all_views(conn=None):

    views = list(
        r.table("views")
        .pluck(ViewKey.Name)
        .run(conn)
    )

    return views


def _db_build_view(data_doc):
    """ Builds a View instance.

    Based on the data document passed, a View object is built.

    Args:
        data_doc: A dict with data representing a View.

    Returns:
        A View instance.
    """

    if not data_doc:

        return None

    view = View()
    view.name = data_doc.get(ViewKey.Name)

    view.id = data_doc.get(ViewKey.Name)
    view.cpu_throttle = data_doc.get(ViewKey.CpuThrottle)
    view.net_throttle = data_doc.get(ViewKey.NetThrottle)

    if data_doc.get(ViewKey.Users):

        for doc in data_doc[ViewKey.Users]:

            u = _db_document_exist(_id=doc[UserKey.Name],
                                   collection_name=UserCollection)

            if u:

                u = User(doc[ViewKey.Name])

                view.add_user(u)

    if data_doc.get(ViewKey.Groups):

        for doc in data_doc[ViewKey.Groups]:

            g = _db_document_exist(_id=doc[GroupKey.Id],
                                   collection_name=GroupCollection)

            if g:

                g = Group(doc[GroupKey.Name])
                g.id = doc[GroupKey.Id]

                view.add_group(g)

    return view


def _db_build_group(data_doc):
    """ Builds a Group instance.

    Based on the data document passed, a Group object is built.

    Args:
        data_doc: A dict with data representing a group.

    Returns:
        A Group instance.
    """

    if not data_doc:

        return None

    group = Group()
    group.name = data_doc.get(GroupKey.Name)
    group.id = data_doc.get(GroupKey.Id)

    if data_doc.get(GroupKey.Permissions):

        for perm in data_doc.get(GroupKey.Permissions):

            group.add_permission(perm)

    if data_doc.get(GroupKey.View):

        c = _db_document_exist(
            _id=data_doc[GroupKey.View][ViewKey.Name],
            collection_name=ViewCollection
        )

        if c:

            c = View(data_doc[GroupKey.View][ViewKey.Name])

            group.set_view(c)

    if data_doc.get(GroupKey.Users):

        for doc in data_doc[GroupKey.Users]:

            u = _db_document_exist(_id=doc[UserKey.Name],
                                   collection_name=UserCollection)

            if u:

                u = User(doc[UserKey.Name])

                group.add_user(u)

    return group


def _db_build_user(data_doc):
    """ Builds a User instance.

    Based on the data document passed, a User object is built.

    Args:
        data_doc: A dict with data representing a User.

    Returns:
        A User instance.
    """

    if not data_doc:

        return None

    user = User()
    user.name = data_doc.get(UserKey.Name)
    user.id = user.name

    user.full_name = data_doc.get(UserKey.FullName)
    user.password = data_doc.get(UserKey.Password)
    user.email = data_doc.get(UserKey.Email)
    user.enabled = data_doc.get(UserKey.Enabled)

    if data_doc.get(UserKey.Groups):

        for doc in data_doc[UserKey.Groups]:

            g = _db_document_exist(_id=doc[GroupKey.Id],
                                   collection_name=GroupCollection)

            if g:

                g = Group(doc[GroupKey.Name])
                g.id = doc[GroupKey.Id]

                user.add_group(g)

    if data_doc.get(UserKey.Views):

        for doc in data_doc[UserKey.Views]:

            c = _db_document_exist(_id=doc[ViewKey.Name],
                                   collection_name=ViewCollection)

            if c:

                c = View(doc[ViewKey.Name])

                user.add_view(c)

    if data_doc.get(UserKey.CurrentView):

        current_view = data_doc[UserKey.CurrentView]

        c = _db_document_exist(_id=current_view[ViewKey.Name],
                               collection_name=ViewCollection)

        if c:

            c = View(current_view[ViewKey.Name])

            user.set_current_view(c)

    if data_doc.get(UserKey.DefaultView):

        default_view = data_doc[UserKey.DefaultView]

        c = _db_document_exist(_id=default_view[ViewKey.Name],
                               collection_name=ViewCollection)

        if c:

            c = View(default_view[ViewKey.Name])

            user.set_default_view(c)

    return user

@db_create_close
def _db_save(_id=None, collection_name=None, data=None, conn=None):
    """Attempts to save data to the DB.

    If an document ID is provided, then the document gets updated. Otherwise
    a new document is inserted.

    Args:

        _id: Id representing a document if it has one.

        collection_name: Name of the collection to be used.

        data: Data to be inserted or replaced.

    Returns:

        A DB generated ID is returned (empty string if no ID is available)
            on successful insert, False otherwise.
        A boolean True if updating was successful, False otherwise.

    """

    success = False

    if _id:

        result = (
            r.table(collection_name)
            .get(_id)
            .update(data)
            .run(conn)
        )

        if result.get('replaced') and result.get('replaced') > 0:

            success = True

    else:

        result = r.table(collection_name).insert(data).run(conn)

        if result.get('inserted') and result.get('inserted') > 0:

            if 'generated_keys' in result:

                success = result['generated_keys'][0]

            else:

                success = ''

    return success

@db_create_close
def _db_get(collection_name=None, _id=None, _filter=None, conn=None):
    """Attempts to get data from the DB.

    Tries to get a document based on the id. If a filter is used, then a list
    of documents is returned that match said filter.

    Args:

        collection_name: Name of the collection to be used.

        _id: Id (primary key) representing a document.

        _filter: A dict type that contains key(s)/value(s) of the
            document to get.

    Returns:

        If the document id is provided, then that document is returned.
        If a filter is used, then a list of documents is returned.

    """

    document = None

    if _id:

        document = r.table(collection_name).get(_id).run(conn)

    else:

        document = list(r.table(collection_name).filter(_filter).run(conn))

    return document

@db_create_close
def _db_delete(collection_name=None, _id=None, conn=None):
    """Attempts to delete data from the DB.

    Tries to delete a document based on the id or filter provided. If filter is
    used, the first document returned is deleted.

    Args:

        collection_name: Name of the collection to be used.

        _id: Id (primary key) representing a document

    Returns:

        True if document was deleted, False otherwise.

    """

    success = None

    if _id:

        result = r.table(collection_name).get(_id).delete().run(conn)

        if 'deleted' in result and result['deleted'] > 0:

            success = True

    return success


def save_view(view):
    """Saves the view to DB.

    If an id attribute is found, the document representing that id is updated.
    Otherwise we create a new document.

    Args:

        view: A View instance.

    Returns:

        True is view was saved successfully, False otherwise.

    """

    _view = {}

    _view[ViewKey.Name] = view.name
    _view[ViewKey.NetThrottle] = view.net_throttle
    _view[ViewKey.CpuThrottle] = view.cpu_throttle

    _view[ViewKey.Groups] = view.get_groups(raw=True)

    _view[ViewKey.Users] = view.get_users(raw=True)

    success = _db_save(_id=view.id, collection_name=ViewCollection,
                       data=_view)

    return success


def save_user(user):
    """Saves the user to DB.

    If an id attribute is found, the document representing that id is updated.
    Otherwise we create a new document.

    Args:

        user: A User instance.

    Returns:

        True is view was saved successfully, False otherwise.

    """

    _user = {}

    _user[UserKey.Name] = user.name
    _user[UserKey.FullName] = user.full_name
    _user[UserKey.Email] = user.email
    _user[UserKey.Enabled] = user.enabled
    _user[UserKey.Password] = user.password

    _user[UserKey.Groups] = user.get_groups(raw=True)

    _user[UserKey.Views] = user.get_views(raw=True)
    _user[UserKey.CurrentView] = user.get_current_view(raw=True)
    _user[UserKey.DefaultView] = user.get_default_view(raw=True)

    success = _db_save(_id=user.id, collection_name=UserCollection, data=_user)

    return success


def save_group(group):
    """Saves the group to DB.

    If an id attribute is found, the document representing that id is updated.
    Otherwise we create a new document.

    Args:

        group: A Group instance.

    Returns:

        True is view was saved successfully, False otherwise.

    """

    _group = {}

    _group[GroupKey.Name] = group.name
    _group[GroupKey.View] = group.get_view(raw=True)
    _group[GroupKey.Permissions] = group.get_permissions()

    _group[GroupKey.Users] = group.get_users(raw=True)

    success = _db_save(_id=group.id, collection_name=GroupCollection,
                       data=_group)

    return success


def get_view(name=None):
    """Gets the View from the DB.

    Based on the id or name given, retrieve said view.

    Args:

        _id: Id representing the view to retrieve.

        name: Name representing the view to retrieve.

    Returns:

        A View instance.

    """

    data_doc = None

    if name:

        data_doc = _db_get(collection_name=ViewCollection, _id=name)

    if data_doc:

        view = _db_build_view(data_doc)

    else:

        view = None

    return view


def get_user(name=None):
    """Gets the User from the DB.

    Based on the name given, retrieve said user.

    Args:

        name: Name representing the user to retrieve.

    Returns:

        A User instance.

    """
    data_doc = None

    if name:

        data_doc = _db_get(collection_name=UserCollection, _id=name)

    if data_doc:

        user = _db_build_user(data_doc)

    else:

        user = None

    return user


def get_group(_id=None, name=None, all_groups=False):
    """Gets the Group from the DB.

    Based on the id or name given, retrieve said group.

    Args:

        _id: Id representing the group to retrieve.

        name: Name representing the group to retrieve.

        all_groups: True if a list of all groups matching the name is to
            be returned. Does not work with _id.

    Returns:

        A Group instance.

    """

    data_doc = None

    if _id:

        data_doc = _db_get(collection_name=GroupCollection, _id=_id)

    elif name:

        data_doc = _db_get(collection_name=GroupCollection,
                           _filter={GroupKey.Name: name})

        if data_doc:

            if not all_groups:

                data_doc = data_doc[0]

        else:

            data_doc = {}

    if isinstance(data_doc, list):

        groups = []

        for g in data_doc:
            groups.append(_db_build_group(g))

        return groups

    elif data_doc:

        return _db_build_group(data_doc)

    return None

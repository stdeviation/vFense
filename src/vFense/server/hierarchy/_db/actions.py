import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r

from vFense.server.hierarchy import Collection, GroupKey, UserKey, ViewKey
from vFense.server.hierarchy import GroupsPerUserKey, UsersPerViewKey

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@db_create_close
def get_user(user_name=None, conn=None):

    if not user_name:
        return None

    user = (
        r.table(Collection.Users)
        .get(user_name)
        .run(conn)
    )

    return user


@db_create_close
def get_view(view_name=None, conn=None):

    if not view_name:
        return None

    view = (
        r.table(Collection.Views)
        .get(view_name)
        .run(conn)
    )

    return view


#@db_create_close
#def get_group(
#    group_name=None,
#    view_name=None,
#    conn=None
#):
#
#    if(
#        not group_name
#        and not view_name
#    ):
#        return None
#
#        group = db_get_by_secondary(
#            collections=Collection.Groups,
#            values=[
#                    group_name,
#                    view_name
#                ],
#                index=GroupKey.GroupNameAndViewId
#            )
#            .run(conn)
#        )
#
#        if len(group) >= 1:
#            group = group[0]
#        else:
#            group = None
#
#    return group


@db_create_close
def get_views_of_user(user_name=None, conn=None):

    if not user_name:
        return None

    views = (
        r.table(Collection.UsersPerView)
        .get_all(
            user_name,
            index=UsersPerViewKey.UserId
        )
        .pluck(UsersPerViewKey.ViewId)
        .eq_join(
            UsersPerViewKey.ViewId,
            r.table(Collection.Views),
            index=ViewKey.ViewName
        )
        .zip()
        .run(conn)
    )

    c = []
    for view in views:
        c.append(view)

    return c


@db_create_close
def get_users_of_view(view_name=None, conn=None):

    if not view_name:
        return None

    users = (
        r.table(Collection.UsersPerView)
        .get_all(
            view_name,
            index=UsersPerViewKey.ViewId
        )
        .pluck(UsersPerViewKey.UserId)
        .eq_join(
            UsersPerViewKey.UserId,
            r.table(Collection.Users),
            index=UserKey.UserName
        )
        .zip()
        .run(conn)
    )

    u = []
    for user in users:
        u.append(user)

    return u


@db_create_close
def get_users_of_group(
    group_name=None,
    view_name=None,
    conn=None
):

    if (
        not group_name
        and not view_name
    ):
        return None

    user_names = (
        r.table(Collection.GroupsPerUser)
        .get_all(
            [
                group_name,
                view_name
            ],
            index=GroupsPerUserKey.GroupIdAndViewId
        )
        .pluck(GroupsPerUserKey.UserId)
        .run(conn)
    )

    users = []
    for user_name in user_names:

        users.append(
            db_get(
                collection=Collection.Users,
                primary_id=user_name[GroupsPerUserKey.UserId]
            )
        )

    return users


@db_create_close
def get_groups_of_user(
    user_name=None,
    view_name=None,
    conn=None
):

    if (
        not user_name
        and not view_name
    ):
        return None

    group_names = (
        r.table(Collection.GroupsPerUser)
        .get_all(
            [
                user_name,
                view_name
            ],
            index=GroupsPerUserKey.UserIdAndViewId
        )
        .pluck(GroupsPerUserKey.GroupId)
        .run(conn)
    )

    groups = []
    for group_name in group_names:

        groups.extend(
            db_get_by_secondary(
                collection=Collection.Groups,
                values=[
                    group_name[GroupsPerUserKey.GroupId],
                    view_name
                ],
                index=GroupKey.GroupNameAndViewId
            )
        )

    return groups


@db_create_close
def get_groups_of_view(view_name=None, conn=None):

    if not view_name:
        return None

    groups = (
        r.table(Collection.Groups)
        .get_all(
            view_name,
            index=GroupKey.ViewId
        )
        .order_by(GroupKey.GroupName)
        .run(conn)
    )

    g = []
    for group in groups:
        g.append(group)

    return g


#@db_create_close
#def toggle_user_of_view(user=None, view=None, conn=None):
#
#    result = False
#
#    if (
#        not user
#        or not view
#    ):
#        return result
#
#    result = list(
#        r.table(Collection.UsersPerView)
#        .get_all(
#            [user.user_name, view.view_name],
#            index=UsersPerViewKey.UserAndViewId
#        )
#        .run(conn)
#    )
#
#    if len(result) >= 1:
#
#        result = db_delete_by_secondary(
#            Collection.UsersPerView,
#            [user.user_name, view.view_name],
#            UsersPerViewKey.UserAndViewId
#        )
#
#    else:
#
#        res = save_user_per_view(user, view)
#        if res:
#            result = True
#
#    return result
#
#
#@db_create_close
#def toggle_group_of_view(group=None, view=None, conn=None):
#
#    result = False
#
#    if (
#        not group
#        or not view
#    ):
#        return result
#
#    result = list(
#        r.table(Collection.Groups)
#        .get_all(
#            [group.group_name, view.view_name],
#            index=GroupKey.GroupNameAndViewId
#        )
#        .run(conn)
#    )
#
#    if len(result) >= 1:
#
#        result = db_delete_by_secondary(
#            Collection.Groups,
#            [group.group_name, view.view_name],
#            GroupKey.GroupNameAndViewId
#        )
#
#    else:
#
#        res = save_group_per_view(group, view)
#        if res:
#            result = True
#
#    return result
#
#
#@db_create_close
#def toggle_group_of_user(
#    group=None,
#    user=None,
#    view=None,
#    conn=None
#):
#
#    result = False
#
#    if (
#        not group
#        or not user
#        or not view
#    ):
#        return result
#
#    result = list(
#        r.table(Collection.GroupsPerUser)
#        .get_all(
#            [
#                group.group_name,
#                user.user_name,
#                view.view_name
#            ],
#            index=GroupsPerUserKey.GroupUserAndViewId
#        )
#        .run(conn)
#    )
#
#    if len(result) >= 1:
#
#        result = db_delete_by_secondary(
#            Collection.GroupsPerUser,
#            [group.group_name, user.user_name, view.view_name],
#            GroupsPerUserKey.GroupUserAndViewId
#        )
#
#    else:
#
#        res = save_group_per_user(group, user, view)
#        if res:
#            result = True
#
#    return result


@db_create_close
def _db_save(data=None, collection_name=None, conn=None):
    """Attempts to save data to the DB.

    If an document ID is provided, then the document gets updated. Otherwise
    a new document is inserted.

    Args:
        data: Data to be inserted or replaced.

        collection_name: Name of the collection to be used.

        _id: Id representing a document if it has one.

    Returns:

        A DB generated ID is returned (empty string if no ID is available)
            on successful insert, False otherwise.
        A boolean True if updating was successful, False otherwise.

    """

    result = (
        r.table(collection_name)
        .insert(data, upsert=True)
        .run(conn)
    )

    if result.get('inserted') and result.get('inserted') > 0:
        if 'generated_keys' in result:
            return result['generated_keys'][0]

        return True

    if result.get('replaced') and result.get('replaced') > 0:
        return True

    return False


@db_create_close
def db_delete(collection=None, _id=None, conn=None):
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

        result = r.table(collection).get(_id).delete().run(conn)

        if 'deleted' in result and result['deleted'] > 0:

            success = True

    return success


@db_create_close
def db_get(
    collection=None,
    primary_id=None,
    pluck=None,
    conn=None
):
    if (
        not collection
        or not primary_id
    ):
        return None

    query = r.table(collection).get(primary_id)

    if pluck:

        if isinstance(pluck, list):
            doc = query.pluck(*pluck).run(conn)
        else:
            doc = query.pluck(pluck).run(conn)

    else:
        doc = query.run(conn)

    return doc


@db_create_close
def db_get_all(
    collection=None,
    conn=None
):

    result = list(
        r.table(collection)
        .run(conn)
    )

    return result


@db_create_close
def db_get_by_secondary(
    collection=None,
    values=None,
    index=None,
    conn=None
):

    result = list(
        r.table(collection)
        .get_all(
            values,
            index=index
        )
        .run(conn)
    )

    return result


@db_create_close
def db_delete_by_secondary(
    collection=None,
    values=None,
    index=None,
    conn=None
):

    success = False

    result = (
        r.table(collection)
        .get_all(
            values,
            index=index
        )
        .delete()
        .run(conn)
    )

    if 'deleted' in result and result['deleted'] > 0:
            success = True

    return success


@db_create_close
def filter(collection=None, filter_value=None, conn=None):

    if(
        not collection
        or not filter_value
    ):
        return False

    docs = list(
        r.table(collection)
        .filter(filter_value)
        .run(conn)
    )

    return docs


def save_user(user):

    success = _db_save(
        data=user,
        collection_name=Collection.Users
    )

    return success


def save_view(view):
    """Saves the view to DB.

    Args:

        view: View data to be saved.

    Returns:

        True is view was saved successfully, False otherwise.

    """

    success = _db_save(
        data=view,
        collection_name=Collection.Views
    )

    return success


def save_group(group):

    success = _db_save(
        data=group,
        collection_name=Collection.Groups
    )

    return success


def save_group_per_view(data):

    success = _db_save(
        data=data,
        collection_name=Collection.Groups
    )

    return success


def save_group_per_user(data):

    success = _db_save(
        data=data,
        collection_name=Collection.GroupsPerUser
    )

    return success


def save_user_per_view(data):

    success = _db_save(
        data=data,
        collection_name=Collection.UsersPerView
    )

    return success

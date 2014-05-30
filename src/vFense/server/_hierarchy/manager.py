import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

import server.hierarchy._db as _db
from vFense.server.hierarchy.groups import *
from vFense.server.hierarchy.users import *
from vFense.server.hierarchy.views import *

from vFense.server.hierarchy import *
from vFense.server.hierarchy.permissions import Permission
from vFense.utils.security import Crypto

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class Hierarchy():

    @staticmethod
    def get_user(name=None, view=None):
        """Gets a User instance.

        Args:

            name: Name of the user.

            view: View instance to check user against.

        Returns:

            A User instance if found, None otherwise.
        """

        if not name:

            return None

        valid_user = None

        if view:

            users = view.get_users()

            for user in users:

                if user.name == name:

                    valid_user = _db.get_user(name)

        else:

            valid_user = _db.get_user(name)

        return valid_user

    @staticmethod
    def get_users(view=None):
        """Gets all of the user's belonging to a View.

        Args:

            view: View instance to check users against.

        Returns:

            A list of users.
        """

        if not view:

            return None

        view_users = view.get_users()
        users = []

        for user in view_users:

            u = _db.get_user(user.name)

            if u:

                users.append(u)
        return users

    @staticmethod
    def get_group(group=None):
        """Gets a Group instance.

        Args:

            group: A dict consisting of either an id key or name key
                describing the group.

        Returns:

            A Group instance if found, None otherwise.
        """

        if(
            not group
            or not isinstance(group, dict)
            or not (
                group.get(GroupKey.Id) or group.get(GroupKey.Name)
            )
        ):
            return None

        if group.get('id'):

            g = _db.get_group(_id=group[GroupKey.Id])

        else:

            g = _db.get_group(name=group[GroupKey.Name])

        return g

    @staticmethod
    def get_groups(name=None):
        """Gets a list of Group instances.

        Args:

            name: Name of the groups wanted.

        Returns:

            A list of Group instances if found, empty list otherwise.
        """

        if not name:
            return []

        g = _db.get_group(name=name, all_groups=True)

        return g

    @staticmethod
    def get_view(name=None):
        """Gets a View instance.

        Args:

            name: Name of the view.

        Returns:

            A View instance if found, None otherwise.
        """

        if not name:

            return None

        view = _db.get_view(name)

        return view

    @staticmethod
    def create_user(name=None, full_name=None, email=None, password=None,
                    groups=None, views=None, default_view=None):
        """Create a new User and save it.

        All parameters are required *except* groups and views.

        Args:

            name: Name of the user.

            full_name: Full name of the user (ie First and last name).

            email: User's email address.

            password: User's plain text password.

            groups: A list of dicts consisting of either an id key or name key
                describing the group.

            views: Views this user should be added to. List of view
                names.

            default_view: The default view for this user. Will be the
                first data available to the user.

        Returns:

            The newly created User if added successfully, None otherwise.
        """
        if (
            not name
            or not password
        ):
            return False

        # Get the Group instances that will be added to this user.
        if groups:

            groups_list = []

            for group in groups:

                g = Hierarchy.get_group(group)

                if g:

                    groups_list.append(g)

            groups = groups_list

        else:

            groups = []

            g = Hierarchy.get_group({GroupKey.Name: 'Read Only'})

            if g:

                groups.append(g)

        # Get the View instances that will be added to this user.
        if views:

            views_list = []

            for view in views:

                c = Hierarchy.get_view(view)

                if c:

                    views_list.append(c)

            if views_list:
                views = views_list

            else:
                views = [Hierarchy.get_view(DefaultView)]

        else:

            views = [Hierarchy.get_view(DefaultView)]

        if default_view:

            default_view = Hierarchy.get_view(default_view)

        else:

            default_view = views[0]

        name = name.strip()
        full_name = full_name.strip()

        password = Crypto.hash_bcrypt(password)

        user = User(name, full_name, email, password, groups, views,
                    default_view=default_view,
                    current_view=default_view)

        _id = _db.save_user(user)

        if _id == '':

            user.id = user.name

            for g in groups:

                _, mod_group = Hierarchy.toggle_user_from_group(user, g)

                _db.save_group(mod_group)

            for c in views:

                _, mod_view = Hierarchy.toggle_user_from_view(user, c)
                _db.save_view(mod_view)

            return user

        return None

    @staticmethod
    def create_group(
        name=None,
        permissions=None,
        view=None
    ):
        """Create a new Group and save it.

        Args:

            name: Name of the group.

            permissions: List of permissions.Permission constants.

        Returns:

            The newly created Group if added successfully, None otherwise.
        """

        if not name:

            return False

        name = name.strip()

        if not permissions:

            permissions = []

        group = Group(name, permissions)

        _id = _db.save_group(group)

        if _id:

            group.id = _id

            if not view:
                view = DefaultView

            default_view = Hierarchy.get_view(view)
            if default_view:

                group, default_view = Hierarchy.toggle_group_from_view(
                    group,
                    default_view,
                    both=True
                )

                Hierarchy.save_view(default_view)
                Hierarchy.save_group(group)

            return group

        return None

    @staticmethod
    def default_groups(view=None):
        Hierarchy.create_group('Administrator', [Permission.Admin], view)
        Hierarchy.create_group('Read Only', view=view)
        Hierarchy.create_group('Install Only', [Permission.Install], view)

    @staticmethod
    def create_view(name=None):
        """Create a new View and save it.

        Args:

            name: Name of the view.

        Returns:

            The newly created View if added successfully, None otherwise.
        """

        if not name:

            return False

        name = name.strip()

        view = View(name)

        _id = _db.save_view(view)

        if _id == '':

            view.id = view.name
            return view

        return None

    @staticmethod
    def edit_user(user=None, mod_data=None):
        """Edit user properties.

        Args:

            user: Name of the user.

            mod_data: A dic of UserKeys as the key with the new values.

        Returns:

            True if successful, False otherwise.
        """

        if not user and not mod_data:

            return False

        user = Hierarchy.get_user(user)

        password = mod_data.get(UserKey.Password)
        if password:

            user.password = Crypto.hash_bcrypt(password)

        full_name = mod_data.get(UserKey.FullName)
        if full_name:

            user.full_name = full_name

        email = mod_data.get(UserKey.Email)
        if email:

            user.email = email

        current_view = mod_data.get(UserKey.CurrentView)
        if current_view:

            view = Hierarchy.get_view(current_view)

            if view:

                view_name = ''
                current_view = user.get_current_view()
                if current_view:
                    view_name = current_view.name

                if not view.name == view_name:
                    user.set_current_view(view)

        default_view = mod_data.get(UserKey.DefaultView)
        if default_view:

            view = Hierarchy.get_view(default_view)

            if view:

                user.set_current_view(view)

        views = mod_data.get(UserKey.Views)
        if views:

            for view in views:

                c = Hierarchy.get_view(view)

                if c:

                    user, c = Hierarchy.toggle_user_from_view(
                        user,
                        c,
                        both=True
                    )

                    _db.save_view(c)

        groups = mod_data.get(UserKey.Groups)

        if groups:

            for group in groups:

                g = Hierarchy.get_group(group)

                if g:

                    user, g = Hierarchy.toggle_user_from_group(user, g,
                                                               both=True)

                    _db.save_group(g)

        if _db.save_user(user):

            return True

        return False

    @staticmethod
    def edit_view(name, mod_data=None):
        """Edit view properties.

        Args:

            name: Name of the view.

            mod_data: A dic of GroupKeys as the key with the new values.

        Returns:

            True if successful, False otherwise.
        """

        if not name and not mod_data:

            return False

        view = Hierarchy.get_view(name)

        net_throttle = mod_data.get(ViewKey.NetThrottle)
        if net_throttle:

            view.net_throttle = net_throttle

        cpu_throttle = mod_data.get(ViewKey.CpuThrottle)
        if cpu_throttle:

            view.cpu_throttle = cpu_throttle

        groups = mod_data.get(ViewKey.Groups)
        if groups:

            for group in groups:

                g = Hierarchy.get_group(group)

                if g:

                    g, view = Hierarchy.toggle_group_from_view(
                        g,
                        view, both=True)

                    _db.save_group(g)

        users = mod_data.get(ViewKey.Users)
        if users:

            for user in users:

                u = Hierarchy.get_user(user)

                if u:

                    u, view = Hierarchy.toggle_user_from_view(
                        u,
                        view, both=True
                    )

                    _db.save_user(u)

        return _db.save_view(view)

    @staticmethod
    def edit_group(group=None, mod_data=None):
        """Edit group's properties.

        Args:

            group: the Group instance to edit.

            mod_data: A dic of GroupKeys as the key with the new values.

        Returns:

            True if successful, False otherwise.
        """

        if not group and not mod_data:

            return False

        view = mod_data.get(GroupKey.View)
        if view:

            c = Hierarchy.get_view(view)

            if c:

                group.set_view(c)

        permissions = mod_data.get(GroupKey.Permissions)
        group_permissions = group.get_permissions()
        if permissions:

            for perm in permissions:

                if perm in group_permissions:

                    group.remove_permission(perm)

                else:

                    group.add_permission(perm)

        users = mod_data.get(GroupKey.Users)
        if users:

            new_users = []
            for user in users:

                u = Hierarchy.get_user(user)
                if u:

                    new_users.append(u)

            for user in new_users:

                user, group = Hierarchy.toggle_user_from_group(user,
                                                               group,
                                                               both=True)

                Hierarchy.save_user(user)

        return Hierarchy.save_group(group)

    # Famous toggle functions!!
    @staticmethod
    def toggle_user_from_group(user=None, group=None, both=False):
        """Toggles the user for the group.

         If the user is part of group then it's removed. If the user is not
         part of the group then it's added. Changes are not saved to the DB.

         Args:

            user: A User instance.

            group: A Group instance.

            both: Whether to toggle both User and Group instances or
                just group.

        Returns:

            True if successfully toggled, False otherwise.
        """

        users_in_group = group.get_users()
        user_found = False

        for uig in users_in_group:

            if user.name == uig.name:

                user_found = True
                break

        if user_found:

            if both:
                user.remove_group(group)

            group.remove_user(user)

        else:

            if both:
                user.add_group(group)

            group.add_user(user)

        return user, group

    @staticmethod
    def toggle_user_from_view(user=None, view=None, both=False):
        """Toggles the user for the view.

         If the user is part of view then it's removed. If the user is not
         part of the view then it's added. Changes are not saved to the DB.

         Args:

            user: A User instance.

            view: A View instance.

            both: Whether to toggle both User and View instances or
                just view.

        Returns:

            True if successfully toggled, False otherwise.
        """

        users_in_view = view.get_users()

        user_found = False

        for uic in users_in_view:

            if user.name == uic.name:

                user_found = True
                break

        if user_found:

            if both:
                user.remove_view(view)

            view.remove_user(user)

        else:

            if both:
                user.add_view(view)

            view.add_user(user)

        return user, view

    @staticmethod
    def toggle_group_from_view(group=None, view=None, both=False):
        """Toggles the group for the view.

         If the group is part of view then it's removed. If the group is
         not part of the view then it's added. Changes are not saved
         to the DB.

         Args:

            group: A Group instance.

            view: A View instance.

            both: Whether to toggle both Group and View instances or just
                view.

        Returns:

            True if successfully toggled, False otherwise.
        """

        group_in_view = view.get_groups()
        group_found = False

        for gic in group_in_view:

            if group.id == gic.id:

                group_found = True
                break

        if group_found:

            if both:
                group.clear_view()

            view.remove_group(group)

        else:

            if both:
                group.set_view(view)

            view.add_group(group)

        return group, view

    @staticmethod
    def delete_user(name=None, current_view=None):
        """Delete a User for good.

         Args:

            name: Name of the user to delete.

        Returns:

            True if user was deleted, False otherwise.
        """

        if name == 'admin':
            return False

        user = Hierarchy.get_user(name)

        if not name:

            return False

        # Build users and groups list before deleting user.
        user_groups = user.get_groups()
        found_groups = []

        for group in user_groups:

            g = Hierarchy.get_group({GroupKey.Id: group.id})

            if g:

                found_groups.append(g)

        user_views = user.get_views()
        found_views = []

        for view in user_views:

            c = Hierarchy.get_view(view.name)

            if c:

                found_views.append(c)

        deleted = _db._db_delete(collection_name=UserCollection, _id=name)

        if deleted:

            for group in found_groups:

                __, group = Hierarchy.toggle_user_from_group(user, group)

                _db.save_group(group)

            for view in found_views:

                __, view = Hierarchy.toggle_user_from_view(user,
                                                                   view)

                _db.save_view(view)

        return deleted

    @staticmethod
    def delete_group(group=None):
        """Delete a Group for good.

         Args:

            group: Group instance to delete.

        Returns:

            True if group was deleted, False otherwise.
        """

        if not group:

            return False

        if group.name == 'Administrator':

            return False

        # Build users and view list before deleting group.
        group_users = group.get_users()
        found_users = []

        for user in group_users:

            u = Hierarchy.get_user(user.name)

            if u:

                found_users.append(u)

        view = group.get_view()
        view = Hierarchy.get_view(view.name)

        deleted = _db._db_delete(collection_name=GroupCollection, _id=group.id)

        if deleted:

            for user in found_users:

                user, __ = Hierarchy.toggle_user_from_group(user, group)

                Hierarchy.save_user(user)

            if view:

                __, view = Hierarchy.toggle_group_from_view(
                    group,
                    view
                )

                Hierarchy.save_view(view)

        return deleted

    @staticmethod
    def delete_view(name=None):
        """Delete a View for good.

         Args:

            name: Name of the view to delete.

        Returns:

            True if view was deleted, False otherwise.
        """

        if(
            not name
            or name == 'default'
        ):
            return False

        view = Hierarchy.get_view(name)

        # Build users and groups list before deleting view.
        view_groups = view.get_groups()
        found_groups = []

        for group in view_groups:

            g = Hierarchy.get_group({GroupKey.Id: group.id})

            if g:

                found_groups.append(g)

        view_users = view.get_users()
        found_users = []

        for user in view_users:

            u = Hierarchy.get_user(user.name)

            if u:

                found_users.append(u)

        deleted = _db._db_delete(collection_name=ViewCollection,
                                 _id=view.name)

        if deleted:

            for group in found_groups:

                group, __ = Hierarchy.toggle_group_from_view(
                    group,
                    view,
                    both=True
                )

                _db.save_group(group)

            for user in found_users:

                user, __ = Hierarchy.toggle_user_from_view(
                    user,
                    view,
                    both=True
                )

                _db.save_user(user)

        return deleted

    @staticmethod
    def save_user(user=None):

        if user:

            return _db.save_user(user)

    @staticmethod
    def save_view(view=None):

        if view:

            return _db.save_view(view)

    @staticmethod
    def save_group(group=None):

        if group:

            return _db.save_group(group)

    @staticmethod
    def authenticate_account(name=None, password=''):

        if name:

            user = Hierarchy.get_user(name)

            if user:

                hash_password = user.password.encode('utf-8')

                if Crypto.verify_bcrypt_hash(password, hash_password):

                    return True

        return False


def get_current_view_name(user):
    """Gets the current view name for a user.

     Args:

        name: Name of the user.

    Returns:

        The name of the current view if it's found. Default view
            otherwise.
    """

    user = Hierarchy.get_user(user)

    if user:

        view = user.get_current_view()

        if view:

            return view.name

    return DefaultView


def get_all_views():

    return _db.get_all_views()

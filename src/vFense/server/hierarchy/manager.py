import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.utils.security import generate_pass
from vFense.server.hierarchy import *
from vFense.server.hierarchy._db import actions
from vFense.server.hierarchy.group import Group
from vFense.server.hierarchy.user import User
from vFense.server.hierarchy.view import View

from vFense.server.hierarchy.permissions import Permission
from vFense.utils.security import Crypto

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class Hierarchy():

    @staticmethod
    def get_user(user_name=None):
        """Gets a User instance.

        Args:

            name: Name of the user.

        Returns:

            A User instance if found, None otherwise.
        """

        if not user_name:

            return None

        user = None

        try:

            u = actions.get_user(user_name)
            if u:

                user = User(
                    u[UserKey.UserName],
                    u[UserKey.Password],
                    u[UserKey.FullName],
                    u[UserKey.Email],
                    u[UserKey.CurrentView],
                    u[UserKey.DefaultView],
                    u[UserKey.Enabled]
                )

        except Exception as e:
            logger.error('Could not get user %s.' % user_name)
            logger.exception(e)

        return user

    @staticmethod
    def get_views_of_user(user_name=None):

        if not user_name:
            return None

        views = []

        try:

            if user_name == AdminUser:

                all_views = actions.db_get_all(
                    Collection.Views
                )

            else:

                all_views = actions.get_views_of_user(
                    user_name=user_name
                )

            for c in all_views:
                try:
                    view = View(
                        c[ViewKey.ViewName],
                        c[ViewKey.Properties],
                    )

                    views.append(view)

                except Exception as e:
                    logger.error('Skipping view `%s`' % u)
                    logger.exception(e)

        except Exception as e:

            logger.error(
                'Could not get views of user `%s` .'
                % user_name
            )
            logger.exception(e)

        return views

    @staticmethod
    def get_users_of_group(group_name=None, view_name=None):
        """Gets all of the user's belonging to a group.

        Returns:

            A list of users.
        """

        if (
            not group_name
            and not view_name
        ):

            return None

        users = []
        try:

            group_users = actions.get_users_of_group(
                group_name=group_name,
                view_name=view_name
            )

            for u in group_users:
                try:
                    user = User(
                        u[UserKey.UserName],
                        u[UserKey.Password],
                        u[UserKey.FullName],
                        u[UserKey.Email],
                        u[UserKey.CurrentView],
                        u[UserKey.DefaultView],
                        u[UserKey.Enabled]
                    )

                    users.append(user)

                except Exception as e:
                    logger.error('Skipping user %s' % u)
                    logger.exception(e)

        except Exception as e:

            logger.error(
                'Could not get users of group "%s" .'
                % group_name
            )
            logger.exception(e)

        return users

    @staticmethod
    def get_users_of_view(view_name=None):
        """Gets all of the user's belonging to a View.

        Args:

            view: View name to check users against.

        Returns:

            A list of users.
        """

        if not view_name:

            return None

        users = []
        try:

            view_users = actions.get_users_of_view(
                view_name=view_name
            )

            for u in view_users:
                try:
                    user = User(
                        u[UserKey.UserName],
                        u[UserKey.Password],
                        u[UserKey.FullName],
                        u[UserKey.Email],
                        u[UserKey.CurrentView],
                        u[UserKey.DefaultView],
                        u[UserKey.Enabled]
                    )

                    users.append(user)

                except Exception as e:
                    logger.error('Skipping user %s' % u)
                    logger.exception(e)

        except Exception as e:

            logger.error(
                'Could not get users of view "%s" .'
                % view_name
            )
            logger.exception(e)

        return users

    @staticmethod
    def get_group(group_name=None, view_name=None):
        """Gets a Group instance.

        Args:


        Returns:

            A Group instance if found, None otherwise.
        """
        if(
            not group_name
            and not view_name
        ):
            return None

        group = actions.db_get_by_secondary(
            collection=Collection.Groups,
            values=[
                group_name,
                view_name
            ],
            index=GroupKey.GroupNameAndViewId
        )

        if len(group) >= 1:
            for gp in group:
                if gp[GroupKey.ViewId] == view_name:
                    g = gp
                    break

            g = group[0]

        else:
            g = None

        if g:

            group = Group(
                g[GroupKey.GroupName],
                g[GroupKey.ViewId],
                g[GroupKey.Permissions],
                g[GroupKey.Id]
            )

            return group

        return None

    @staticmethod
    def get_group_by_id(group_id=None):
        """Gets a Group instance.

        Args:


        Returns:

            A Group instance if found, None otherwise.
        """
        if not group_id:
            return None

        try:

            g = actions.db_get(
                collection=Collection.Groups,
                primary_id=group_id
            )

            if g:

                group = Group(
                    g[GroupKey.GroupName],
                    g[GroupKey.ViewId],
                    g[GroupKey.Permissions],
                    g[GroupKey.Id]
                )

                return group

        except Exception as e:

            logger.error('Could not get group by id `%s`' % group_id)
            logger.exception(e)

        return None

    @staticmethod
    def get_groups_of_user(user_name=None, view_name=None):
        """Gets the groups of a user.

        Args:

            name: Name of the groups wanted.

        Returns:

            A list of Group instances if found, empty list otherwise.
        """

        if(
            not view_name
            and not user_name
        ):
            return []

        g = []
        try:

#            if Hierarchy.is_admin(user_name):
#
#                print 'getting all groups'
#
#                groups = Hierarchy.get_groups_of_view(
#                    view_name
#                )
#
#                g = groups
#
#            else:

                groups = actions.get_groups_of_user(
                    user_name=user_name,
                    view_name=view_name
                )

                for group in groups:
                    try:

                        tmp = Group(
                            group[GroupKey.GroupName],
                            group[GroupKey.ViewId],
                            group[GroupKey.Permissions],
                            group[GroupKey.Id]
                        )
                        g.append(tmp)

                    except Exception as e:

                        logger.error('Skipping group %s.' % group)
                        logger.exception(e)

        except Exception as e:

            logger.error(
                'Could not get groups of user `%s`.'
                % user_name
            )
            logger.exception(e)

        return g

    @staticmethod
    def get_groups_of_view(view_name=None):
        """Gets the groups of a view.

        Args:

            name: Name of the view.

        Returns:

            A list of Group instances if found, empty list otherwise.
        """

        if not view_name:
            return []

        g = []
        try:

            groups = actions.get_groups_of_view(
                view_name=view_name
            )

            for group in groups:
                try:

                    tmp = Group(
                        group[GroupKey.GroupName],
                        group[GroupKey.ViewId],
                        group[GroupKey.Permissions],
                        group[GroupKey.Id]
                    )
                    g.append(tmp)

                except Exception as e:

                    logger.error('Skipping group %s.' % group)
                    logger.exception(e)

        except Exception as e:

            logger.error(
                'Could not get groups of view `%s`.'
                % view_name
            )
            logger.exception(e)

        return g

    @staticmethod
    def get_view(view_name=None):
        """Gets a View instance.

        Args:

            name: Name of the view.

        Returns:

            A View instance if found, None otherwise.
        """

        if not view_name:
            return None

        view = None
        c = actions.get_view(view_name=view_name)

        if c:

            view = View(
                c[ViewKey.ViewName],
                c[ViewKey.Properties]
            )

        return view

    @staticmethod
    def create_user(
        user_name=None,
        full_name=None,
        email=None,
        password=None,
        groups=None,
        default_view=None,
        views=None
    ):
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
            not user_name
        ):
            return False, "Username/password is needed."

        try:

            if Hierarchy.get_user(user_name):
                return False, (
                    "Username `%s` already exist." % user_name
                )

            # Get the View(s) that will be added to this user.
            views_to_add = []
            if views:

                for view_name in views:

                    c = Hierarchy.get_view(view_name)

                    if c:

                        views_to_add.append(c)

            if default_view:

                defult_cusomter = Hierarchy.get_view(default_view)
                add_view = True

                if default_view:

                    for c in view_to_add:
                        if c.view_name == dc.view_name:
                            add_view = False
                            break

                    if add_view:
                        views_to_add.append(default_cusotmer)

            else:

                if views_to_add:

                    default_view = views_to_add[0]

                else:

                    default_view = Hierarchy.get_view(DefaultView)
                    views_to_add.append(default_view)

            #if not views:
            #    views = [default_view]

            #if added_default:
            #    if DefaultView not in views:
            #        views.append(DefaultView)

            # Now a View type.
            #default_view = Hierarchy.get_view(default_view)

            #if not views_to_add:
            #    views_to_add.append(default_view)

            #############################################################

            # Get the Group(s) that will be added to this user.
            groups_to_add = []
            if groups:

                groups_list = []

                for group_name in groups:

                    g = Hierarchy.get_group(
                        group_name,
                        default_view.view_name
                    )

                    if g:

                        groups_list.append(g)

                groups_to_add.extend(groups_list)

            else:

                g = Hierarchy.get_group(
                    DefaultGroup.ReadOnly,
                    default_view.view_name
                )

                if g:

                    groups_to_add.append(g)
            #############################################################

            user_name = user_name.strip()
            full_name = full_name.strip()

            if not password:
                password = generate_pass()

            password = Crypto.hash_bcrypt(password.encode('utf-8'))

            user = User(
                user_name,
                password,
                full_name,
                email,
                default_view.view_name,
                default_view.view_name
            )

            saved = Hierarchy.save_user(user)

            if saved:

                for group in groups_to_add:

                    Hierarchy.toggle_group_of_user(
                        group=group,
                        user=user,
                        view=default_view
                    )

                for view in views_to_add:

                    Hierarchy.toggle_user_from_view(
                        user=user,
                        view=view
                    )

                return user, ''

        except Exception as e:

            logger.error("Unable to create user `%s`." % user_name)
            logger.exception(e)

        return None

    @staticmethod
    def create_group(
        name=None,
        permissions=None,
        view_name=None
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

        if not view_name:
                view_name = DefaultView

        if Hierarchy.get_group(name, view_name):
            return False, (
                "Group with name `%s` already exist for view `%s`"
                % (name, view_name)
            )

        name = name.strip()

        if not permissions:
            permissions = []

        view = Hierarchy.get_view(view_name)
        if not view:
            return None, "View `%s` does not exist." % view_name

        group = Group(name, view_name, permissions)
        saved = Hierarchy.save_group(group)

        if saved:

            # No need to toggle because its added during the save.
            #view = Hierarchy.get_view(view_name)
            #if view:

            #    toggled = Hierarchy.toggle_group_from_view(
            #        group,
            #        view,
            #    )

            group.id = saved
            return group, ""

        return None, "Unable to create group `%s`" % name

    @staticmethod
    def default_groups(view_name=None):

        try:

            admin = Hierarchy.create_group(
                DefaultGroup.Administrator,
                [Permission.Admin],
                view_name
            )

            read = Hierarchy.create_group(
                DefaultGroup.ReadOnly,
                view_name=view_name
            )

            install = Hierarchy.create_group(
                DefaultGroup.InstallOnly,
                [Permission.Install],
                view_name
            )

            success = admin[0] and read[0] and install[0]
            msg = admin[1] + read[1] + install[1]

            return (success, msg)

        except Exception as e:

            logger.error("Unable to create default groups.")
            logger.exception(e)

            return None

    @staticmethod
    def create_view(name=None, properties={}):
        """Create a new View and save it.

        Args:

            name: Name of the view.

        Returns:

            The newly created View if added successfully, None otherwise.
        """

        if not name:
            return False, "A view name is needed."

        if Hierarchy.get_view(name):
            return False, (
                "View with name `%s` already exist." % name
            )

        name = name.strip()

        view = View(name, properties)
        results = Hierarchy.save_view(view)

        if results:
            Hierarchy.default_groups(name)
            return view, ""

        return None, (
            "Unable to create view `%s`. View already exist?" % name
        )

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
        if not user:
            return False

        password = mod_data.get(UserKey.Password)
        if password:
            password = password.encode('utf-8')
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
                user.current_view = current_view

        default_view = mod_data.get(UserKey.DefaultView)
        if default_view:

            view = Hierarchy.get_view(default_view)

            if view:
                user.default_view = default_view

        views = mod_data.get(UserKey.Views)
        if views:

            for view in views:

                c = Hierarchy.get_view(view)

                if c:

                    Hierarchy.toggle_user_from_view(
                        user,
                        c,
                    )

        groups = mod_data.get(UserKey.Groups)
        if groups:

            view_context = mod_data.get('view_context')
            if view_context:

                c = Hierarchy.get_view(view_context)

            else:

                c = Hierarchy.get_view(user.current_view)

            if c:
                for group in groups:

                    g = Hierarchy.get_group(group)

                    if g:

                        Hierarchy.toggle_group_of_user(
                            user,
                            g,
                            c
                        )

        if Hierarchy.save_user(user):
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

        ### Hacky variables....
        groups_changed = False
        users_changed = False

        try:

            view = Hierarchy.get_view(name)
            if not view:
                return False

            groups = mod_data.get(ViewKey.Groups)
            if groups:

                for group_names in groups:

                    g = Hierarchy.get_group(
                        group_name,
                        view.view_name
                    )

                    if g:

                        Hierarchy.toggle_group_from_view(
                            g,
                            view
                        )
                        groups_changed = True

            users = mod_data.get(ViewKey.Users)
            if users:

                for user in users:

                    u = Hierarchy.get_user(user)

                    if u:

                        Hierarchy.toggle_user_from_view(
                            u,
                            view,
                        )
                        users_changed = True

            ### HACK UNTIL API IS SEPARATED!!! #####
            if(
                not groups_changed
                or not users_changed
            ):
                return True

            return Hierarchy.save_view(view)

        except Exception as e:

            logger.error("Unable to edit view `%s`" % name)
            logger.exception(e)

    @staticmethod
    def edit_group(
        group_name=None,
        view_name=None,
        mod_data=None
    ):
        """Edit group's properties.

        Args:

            group: the Group instance to edit.

            view_context: View which the group belongs to.

            mod_data: A dic of GroupKeys as the key with the new values.

        Returns:

            True if successful, False otherwise.
        """

        if (
            not group_name
            and not view_name
            and not mod_data
        ):

            return False

        group = Hierarchy.get_group(group_name, view_name)

        ### Hacky variables....
        view_changed = False
        perm_changed = False

        # Change group from one view to another!?
        c = None
        view = mod_data.get(GroupKey.ViewId)
        if view:

            c = Hierarchy.get_view(view)

            if c:

                group.set_view(c.view_name)
                view_changed = True

        permissions = mod_data.get(GroupKey.Permissions)
        group_permissions = group.permissions
        if permissions:

            for perm in permissions:

                if perm in group_permissions:

                    group.remove_permission(perm)
                    perm_changed = True

                else:

                    group.add_permission(perm)
                    perm_changed = True

        users = mod_data.get(GroupKey.Users)
        if users:

            new_users = []
            for user in users:

                if user == AdminUser:
                    continue

                u = Hierarchy.get_user(user)
                if u:

                    new_users.append(u)

            for user in new_users:

                c = Hierarchy.get_view(view_name)
                if not c:
                    continue

                Hierarchy.toggle_group_of_user(
                    group,
                    user,
                    c
                )

        ### HACK UNTIL API IS SEPARATED!!! #####
        if(
            not view_changed
            and not perm_changed
        ):
            return True

        return Hierarchy.save_group(group)

    # Famous toggle functions!!
    # Only brave souls shall pass.
    @staticmethod
    def toggle_group_of_user(group=None, user=None, view=None):
        """Toggles the user for the group for a particular view.

         If the user is part of group then it's removed. If the user is not
         part of the group then it's added.

         Args:

            user: A User instance.

            group: A Group instance.

            view: A View instance.

        Returns:

            True if successfully toggled, False otherwise.
        """

        result = False

        try:

            if (
                not group
                or not user
                or not view
            ):
                return result

            result = actions.db_get_by_secondary(
                collection=Collection.GroupsPerUser,
                values=[
                    group.group_name,
                    user.user_name,
                    view.view_name
                ],
                index=GroupsPerUserKey.GroupUserAndViewId
            )

            if len(result) >= 1:

                result = actions.db_delete_by_secondary(
                    collection=Collection.GroupsPerUser,
                    values=[
                        group.group_name,
                        user.user_name,
                        view.view_name
                    ],
                    index=GroupsPerUserKey.GroupUserAndViewId
                )

            else:

                res = Hierarchy.save_group_per_user(group, user, view)
                if res:
                    result = True

            return result

        except Exception as e:

            logger.error(
                "Unable to toggle user `%s` from group `%s`."
                % (user, group)
            )
            logger.exception(e)

        return False

    @staticmethod
    def toggle_user_from_view(user=None, view=None):
        """Toggles the user for the view.

         If the user is part of view then it's removed. If the user is not
         part of the view then it's added. Changes are not saved to the DB.

         Args:

            user: A User instance.

            view: A View instance.

        Returns:

            True if successfully toggled, False otherwise.
        """

        result = False
        try:

            if (
                not user
                or not view
            ):
                return result

            result = actions.db_get_by_secondary(
                collection=Collection.UsersPerView,
                values=[
                    user.user_name,
                    view.view_name
                ],
                index=UsersPerViewKey.UserAndViewId
            )

            if len(result) >= 1:

                result = actions.db_delete_by_secondary(
                    collection=Collection.UsersPerView,
                    values=[
                        user.user_name,
                        view.view_name
                    ],
                    index=UsersPerViewKey.UserAndViewId
                )

                ### SAFETY HACK
                ### Make sure a user has at least one view.
                view_count = actions.db_get_by_secondary(
                    collection=Collection.UsersPerView,
                    values=user.user_name,
                    index=UsersPerViewKey.UserId
                )

                if len(view_count) <= 0:
                    def_view = Hierarchy.get_view(DefaultView)
                    res = Hierarchy.save_user_per_view(user, def_view)
                    if res:
                        result = True

            else:

                res = Hierarchy.save_user_per_view(user, view)
                if res:
                    result = True

        except Exception as e:

            logger.error(
                "Uable to toggle user `%s` from view `%s`"
                % (user, view)
            )
            logger.exception(e)

        return result

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
        try:

            if (
                not group
                or not view
            ):
                return result

            result = actions.db_get_by_secondary(
                collection=Collection.Groups,
                values=[
                    group.group_name,
                    view.view_name
                ],
                index=GroupKey.GroupNameAndViewId
            )

            if len(result) >= 1:

                result = actions.db_delete_by_secondary(
                    collection=Collection.Groups,
                    values=[
                        group.group_name,
                        view.view_name
                    ],
                    index=GroupKey.GroupNameAndViewId
                )

            else:

                res = Hierarchy.save_group_per_view(group, view)
                if res:
                    result = True

        except Exception as e:

            result = False

            logger.error(
                "Uable to toggle group `%s` from view `%s`"
                % (group, view)
            )
            logger.exception(e)

        return result

    @staticmethod
    def delete_user(name=None):
        """Delete a User for good.

         Args:

            name: Name of the user to delete.

        Returns:

            True if user was deleted, False otherwise.
        """

        if name == AdminUser:
            return False, 'Cannot delete the %s user.' % AdminUser

        if not name:
            return False, 'Username was not provided.'

        try:

            user = Hierarchy.get_user(name)
            if not user:
                return False, 'Did not find user `%s`' % name

            deleted = actions.db_delete_by_secondary(
                collection=Collection.UsersPerView,
                values=name,
                index=UsersPerViewKey.UserId
            )
            if not deleted:
                msg = 'Unable to delete users per view.'
                logger.error(msg)

            deleted = actions.db_delete_by_secondary(
                collection=Collection.GroupsPerUser,
                values=name,
                index=GroupsPerUserKey.UserId
            )

            if not deleted:
                msg = 'Unable to delete group per user.'
                logger.error(msg)

            deleted = actions.db_delete(
                collection=Collection.Users,
                _id=name
            )

            if not deleted:
                msg = 'Unable to delete user `%s`' % name
                logger.error(msg)
                return False, msg

            return True, ''

        except Exception as e:

            logger.error("Unable to delete user `%s`" % name)
            logger.exception(e)

        return False, "Unable to delete user `%s`" % name

    @staticmethod
    def delete_group(group_name=None, view_name=None):
        """Delete a Group for good.

        Returns:

            True if group was deleted, False otherwise.
        """

        if (
            not group_name
            and not view_name
        ):
            return False, "Group and view name is needed."

        if group_name in SafeGroups:
            return False, "Can not delete the `%s` group." % group_name

        error_msg = (
            "Unable to delete group `%s` from view `%s`"
            % (group_name, view_name)
        )

        try:

            if not Hierarchy.get_group(group_name, view_name):
                return False, (
                    'Did not find group `%s` for view `%s`'
                    % (group_name, view_name)
                )

            deleted = actions.db_delete_by_secondary(
                collection=Collection.GroupsPerUser,
                values=[
                    group_name,
                    view_name
                ],
                index=GroupsPerUserKey.GroupUserAndViewId
            )

            if not deleted:
                msg = 'Nothing was deleted from group per user.'
                logger.error(msg)

            deleted = actions.db_delete_by_secondary(
                collection=Collection.Groups,
                values=[
                    group_name,
                    view_name
                ],
                index=GroupKey.GroupNameAndViewId
            )

            if not deleted:
                msg = 'Unable to delete group `%s`' % group_name
                logger.error(msg)
                return False, msg
            else:
                return True, ''

        except Exception as e:

            logger.error(error_msg)
            logger.exception(e)

        logger.error(error_msg)

        return False, error_msg

    @staticmethod
    def delete_view(name=None):
        """Delete a View for good.

         Args:

            name: Name of the view to delete.

        Returns:

            True if view was deleted, False otherwise.
        """


        if not name:
            return False, "View name was not provided."


        if name == DefaultView:
            return False, (
                "Can not delete the `%s` view." % DefaultView
            )


        error_msg = "Unable to delete view `%s`." % name

        try:

            if not Hierarchy.get_view(name):
                return False, 'Did not find view `%s`' % name

            deleted = actions.db_delete_by_secondary(
                collection=Collection.Groups,
                values=name,
                index=GroupKey.ViewId
            )

            if not deleted:
                msg = 'Unable to delete groups from view.'
                logger.error(msg)

            deleted = actions.db_delete_by_secondary(
                collection=Collection.UsersPerView,
                values=name,
                index=UsersPerViewKey.ViewId
            )

            if not deleted:
                msg = 'Unable to delete users from view.'
                logger.error(msg)

            deleted = actions.db_delete(
                collection=Collection.Views,
                _id=name
            )

            if not deleted:
                logger.error(error_msg)
                return False, error_msg

            Hierarchy._users_of_delete_view(name)

            return True, ''

        except Exception as e:

            logger.error(error_msg)
            logger.exception(e)

        return False, error_msg

    @staticmethod
    def _users_of_delete_view(view_name=None):

        if not view_name:
            return False

        try:

            users = actions.filter(
                collection=Collection.Users,
                filter_value={
                    UserKey.CurrentView: view_name
                }
            )

            u2 = actions.filter(
                collection=Collection.Users,
                filter_value={
                    UserKey.DefaultView: view_name
                }
            )

            users.extend(u2)
            for u in users:
                changes = False

                user = User.from_dict(u)

                if user.current_view == view_name:
                    user.current_view = DefaultView
                    changes = True

                if user.default_view == view_name:
                    user.default_view = DefaultView
                    changes = True

                if changes:
                    Hierarchy.save_user(user)

        except Exception as e:

            logger.error('Unable to change users of deleted view')
            logger.exception(e)

    @staticmethod
    def save_user(user=None):

        try:

            if user:
                _user = {}

                _user[UserKey.UserName] = user.user_name
                _user[UserKey.FullName] = user.full_name
                _user[UserKey.Email] = user.email
                _user[UserKey.Enabled] = user.enabled
                _user[UserKey.Password] = user.password

                _user[UserKey.CurrentView] = user.current_view
                _user[UserKey.DefaultView] = user.default_view

                return actions.save_user(_user)

        except Exception as e:

            logger.error("Uable to save user: %s" % user)
            logger.exception(e)

        return None

    @staticmethod
    def save_user_per_view(user=None, view=None):

        try:

            if(
                user
                and view
            ):
                data = {
                    UsersPerViewKey.UserId: user.user_name,
                    UsersPerViewKey.ViewId: view.view_name
                }

                return actions.save_user_per_view(data)

        except Exception as e:

            logger.error(
                "Uable to add user `%s` to view `%s`."
                % (user, view)
            )
            logger.exception(e)

        return False

    @staticmethod
    def save_view(view=None):

        try:

            if view:

                _view = {}

                _view[ViewKey.ViewName] = view.view_name
                _view[ViewKey.Properties] = view.properties

                return actions.save_view(_view)

        except Exception as e:

            logger.error('Unable to save view: %s' % view)
            logger.exception(e)

        return None

    @staticmethod
    def save_group(group=None):

        try:

            if group:

                _group = {}

                if group.id:
                    _group[GroupKey.Id] = group.id

                _group[GroupKey.GroupName] = group.group_name
                _group[GroupKey.Permissions] = group.permissions
                _group[GroupKey.ViewId] = group.view

                return actions.save_group(_group)

        except Exception as e:

            logger.error('Unable to save group: %s' % group)
            logger.exception(e)

        return None

    @staticmethod
    def save_group_per_user(group=None, user=None, view=None):

        try:

            if(
                group
                and user
                and view
            ):

                data = {
                    GroupsPerUserKey.GroupId: group.group_name,
                    GroupsPerUserKey.ViewId: view.view_name,
                    GroupsPerUserKey.UserId: user.user_name
                }

                return actions.save_group_per_user(data)

        except Exception as e:

            logger.error(
                "Uable to add user `%s` to group `%s`."
                % (user, group)
            )
            logger.exception(e)

        return False

    @staticmethod
    def save_group_per_view(group=None, view=None):

        try:

            if(
                group
                and view
            ):
                data = {
                    GroupKey.GroupName: group.group_name,
                    GroupKey.ViewId: view.view_name
                }

                return actions.save_group_per_view(data)

        except Exception as e:

            logger.error(
                "Uable to add group `%s` to view `%s`."
                % (group, view)
            )
            logger.exception(e)

        return False

    @staticmethod
    def authenticate_account(name=None, password=''):

        if name:

            user = Hierarchy.get_user(name)

            if user:

                hash_password = user.password.encode('utf-8')
                password = password.encode('utf-8')

                if Crypto.verify_bcrypt_hash(password, hash_password):

                    return True

        return False

    @staticmethod
    def get_view_property(view_name=None, property_name=None):

        if (
            not view_name
            and not property_name
        ):
            return None

        try:

            properties = actions.db_get(
                collection=Collection.Views,
                primary_id=view_name,
                pluck=ViewKey.Properties
            )

            properties = properties[ViewKey.Properties]

            return properties.get(property_name)

        except Exception as e:

            logger.error("Unable to retrieve property `%s`." % property_name)
            logger.exception(e)

        return None

    @staticmethod
    def is_admin(user_name=None, view_name=None):

        if not user_name:
            return False

        try:

            user = Hierarchy.get_user(user_name)
            if not user:
                return False

            if not view_name:
                view_name = user.current_view

            groups = actions.get_groups_of_user(
                user_name=user_name,
                view_name=view_name
            )

            admin_perm = False
            for group in groups:

                if Permission.Admin in group[GroupKey.Permissions]:
                    admin_perm = True
                    break

            if (
                user_name == AdminUser
                or admin_perm
            ):
                return True

        except Exception as e:

            logger.error("Unable to verify `%s` as admin" % user_name)
            logger.exception(e)

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

        if user.current_view:

            return user.current_view

    return DefaultView


def get_all_views():

    views = []
    try:

        cs = actions.db_get_all(
            collection=Collection.Views,
        )

        for c in cs:

            views.append(
                View(
                    c[ViewKey.ViewName],
                    c[ViewKey.Properties]
                )
            )

    except Exception as e:

        logger.error("Unable to get all views")
        logger.exception(e)

    return views

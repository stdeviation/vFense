from vFense.server.hierarchy import *
from vFense.server.hierarchy.manager import *


class User():

    @staticmethod
    def get(
        active_user=None,
        user_info=None,
        view_context=None,
        all_users=False
    ):

        if not active_user:

            return {
                'pass': False,
                'message': 'No user name provided.'
            }

        active_user = Hierarchy.get_user(active_user)
        if not active_user:
            return {
                'pass': False,
                'message': 'Invalid active user'
            }

        if user_info:

            info_user = Hierarchy.get_user(user_info)
            user = User._user_presentation_hack(
                info_user,
                active_user.current_view
            )

            return {
                'pass': True,
                'message': '',
                'data': user
            }

        elif all_users:

            if not view_context:
                view_context = active_user.current_view

            _users = Hierarchy.get_users_of_view(
                view_context
            )

            users = []

            for u in _users:

                users.append(
                    User._user_presentation_hack(
                        u,
                        view_context
                    )
                )

            return {
                'pass': True,
                'message': '',
                'data': users
            }

        else:

            user = User._user_presentation_hack(active_user)

            return {
                'pass': True,
                'message': '',
                'data': user
            }

        return {
            'pass': False,
            'message': 'No users found'
        }

    @staticmethod
    def _user_presentation_hack(user, active_view=None):
        # The word hack is in the method's name.
        # Prepare for the worst!

        user_dict = user.dict()

        views_list = Hierarchy.get_views_of_user(user.user_name)

        if not active_view:
            active_view = user.current_view

        views = []
        for c in views_list:
            is_admin = False

            gpu = Hierarchy.get_groups_of_user(
                user.user_name,
                c.view_name
            )

            for g in gpu:
                if g.group_name == AdminGroup:
                    is_admin = True
                    break

            views.append(
                {
                    'name': c.view_name,
                    'admin': is_admin
                }
            )

        current_view = {
            'name': user.current_view
        }
        default_view = {
            'name': user.default_view
        }

        gpu = Hierarchy.get_groups_of_user(
            user.user_name,
            active_view
        )

        groups = []
        permissions = []
        for g in gpu:

            groups.append(
                {
                    'name': g.group_name,
                    'id': g.id
                }
            )

            permissions.extend(g.permissions)

        permissions = list(set(permissions))

        user_dict[UserKey.Views] = views
        user_dict[UserKey.Permissions] = permissions
        user_dict[UserKey.CurrentView] = current_view
        user_dict[UserKey.DefaultView] = default_view
        user_dict[UserKey.Groups] = groups
        user_dict['username'] = user.user_name

        return user_dict

    @staticmethod
    def edit(**kwargs):

        data = {}

        username = kwargs.get('username')

        data[UserKey.Password] = kwargs.get('password', None)
        data[UserKey.FullName] = kwargs.get('fullname', None)
        data[UserKey.Email] = kwargs.get('email', None)

        data[UserKey.Views] = kwargs.get('view_ids', None)
        data['view_context'] = kwargs.get('view_context', None)

        data[UserKey.DefaultView] = kwargs.get(
            'default_view_id', None)
        data[UserKey.CurrentView] = kwargs.get(
            'current_view_id', None)

        group_names = kwargs.get('group_names', None)
        group_ids = kwargs.get('group_ids', None)
        groups = []

        if group_names:

            for name in group_names:

                groups.append({GroupKey.Name: name})

        if group_ids:

            for _id in group_ids:

                groups.append({GroupKey.Id: _id})

        data[UserKey.Groups] = groups

        result = Hierarchy.edit_user(username, data)

        if result:

            return {
                'pass': True,
                'message': 'User {} was updated.'.format(username)
            }

        return {
            'pass': False,
            'message': 'User {} could not be updated.'.format(username)
        }

    @staticmethod
    def delete(name=None):

        if not name:

            return {
                'pass': False,
                'message': 'No username was given.'
            }

        if name == 'admin':
            return {
                'pass': False,
                'message': 'Admin account cannot be deleted.'
            }

        deleted = Hierarchy.delete_user(name)

        if deleted:

            return {
                'pass': True,
                'message': 'User {} was deleted.'.format(name)
            }

        return {
            'pass': False,
            'message': 'User {} could not be deleted.'.format(name)
        }

    @staticmethod
    def create(**kwargs):

        parameters = {}

        parameters['user_name'] = kwargs.get('username')
        parameters['password'] = kwargs.get('password')
        parameters['full_name'] = kwargs.get('fullname', None)
        parameters['email'] = kwargs.get('email', None)

        if (
            not parameters['user_name']
            or not parameters['password']
        ):
            return {
                'pass': False,
                'message': 'Please provide a username and/or password.'
            }

        parameters['views'] = kwargs.get('view_ids', None)
        parameters['default_view'] = kwargs.get(
            'default_view_id',
            None
        )

        groups = []
        group_names = kwargs.get('group_names', None)
        group_ids = kwargs.get('group_ids', None)

        if group_names:
            groups.extend(group_names)

        if group_ids:

            for group_id in group_ids:

                g = Hierarchy.get_group_by_id(group_id)
                if g:
                    groups.append(g.group_name)

        parameters['groups'] = groups

        user, msg = Hierarchy.create_user(**parameters)

        if user:

            return {
                'pass': True,
                'message': 'User `%s` created' % user.user_name,
                'data': ''
            }

        return {
            'pass': False,
            'message': (
                'User `%s` could not be created. %s'
                % (parameters['user_name'], msg)
            ),
            'data': ''
        }


class View():

    @staticmethod
    def get(name=None, user_name=None):

        if name:
            view = Hierarchy.get_view(name)

            if view:

                return {
                    'pass': True,
                    'message': 'View found.',
                    'data': view.dict()
                }

        elif user_name:

            if Hierarchy.is_admin(user_name):

                _views = get_all_views()
                views = []
                for c in _views:

                    views.append(
                        {'name': c.view_name}
                    )

                return {
                    'pass': True,
                    'message': 'Views found.',
                    'data': views
                }

            user = Hierarchy.get_user(user_name)
            if user:

                _views = Hierarchy.get_views_of_user(user_name)
                views = []
                for c in _views:
                    views.append(c.dict())

                return {
                    'pass': True,
                    'message': 'Views found.',
                    'data': views
                }

        return {
            'pass': False,
            'message': 'Views were not found for user {}.'.format(
                user_name
            )
        }

    @staticmethod
    def edit(**kwargs):

        data = {}
        view_name = kwargs.get('view_name')
        user_name = kwargs.get('user_name')
        users = kwargs.get('users')

        if not view_name:

            return {
                'pass': False,
                'message': 'View name was not provided.'
            }

        if AdminUser in users:
            return {
                'pass': False,
                'message': (
                    '`%s` account has no editable properties.'
                    % AdminUser
                )
            }

        view = Hierarchy.get_view(view_name)
        if not view:

            return {
                'pass': False,
                'message': 'View `%s` was not found' % view_name
            }

#        user_found = False
#        for user in view.get_users():
#
#            if user.name == user_name:
#                user_found = True
#                break
#
#        if not user_found:
#
#            return {
#                'pass': False,
#                'message': 'User {} does not belong to View "{}"'.format(
#                    user_name,
#                    view.name
#                )
#            }

        data['users'] = users

        properties = {}
        net_throttle = kwargs.get('net_throttle')
        if net_throttle:
            properties[CoreProperty.NetThrottle] = net_throttle

        cpu_throttle = kwargs.get('cpu_throttle')
        if cpu_throttle:
            properties[CoreProperty.CpuThrottle] = cpu_throttle

        pkg_url = kwargs.get('pkg_url')
        if pkg_url:
            properties[CoreProperty.PackageUrl] = pkg_url

        data[ViewKey.Properties] = properties

        group_names = kwargs.get('group_names', None)
        group_ids = kwargs.get('group_ids', None)

        groups = []
        if group_names:
            groups.extend(group_names)

        if group_ids:
            for group_id in group_ids:

                g = Hierarchy.get_group_by_id(group_id)
                if g:

                    groups.append(g.group_name)

        data[ViewKey.Groups] = groups

        result = Hierarchy.edit_view(view.view_name, data)

        if result:

            return {
                'pass': True,
                'message': 'View `%s` was updated.' % view_name
            }

        return {
            'pass': False,
            'message': 'View `%s` could not be updated.' % view_name
        }

    @staticmethod
    def delete(name=None, user_name=None):

        if not name:
            return {
                'pass': False,
                'message': 'View name not provided.'
            }

        if name == 'default':
            return {
                'pass': False,
                'message': 'Default view cannot be deleted.'
            }

        view = Hierarchy.get_view(name)
        user = Hierarchy.get_user(user_name)
        if view:

            # *** Leaving this as reference for Miguel ***
            # view_users = view.get_users()

            view_users = \
                Hierarchy.get_users_of_view(view.view_name)

            #user_found = False
            #for cu in view_users:

            #    if cu.user_name == user.user_name:
            #        user_found = True
            #        break

            # TODO: result is being defined but not used anywhere else
            # in this method
            result = None
            #if user_found:

                # TODO: returning success and error on this call
                # but nothing is being done with the error
                #result = Hierarchy.delete_view(view.view_name)

            success, error = \
                Hierarchy.delete_view(view.view_name)

            if success:


                return {
                    'pass': True,
                    'message': 'Views {} deleted.'.format(name)
                }

            else:

                return {
                    'pass': False,
                    'message': 'Views {} could not deleted.'.format(name)
                }

        return {
            'pass': False,
            'message': 'Views {} was not found.'.format(name)
        }

    @staticmethod
    def create(name, user_name):

        # Hack to set new view properites...
        default = Hierarchy.get_view(DefaultView)
        props = default.properties

        view, msg = Hierarchy.create_view(name, props)
        user = Hierarchy.get_user(user_name)

        if view:

            Hierarchy.toggle_user_from_view(
                user,
                view,
            )

            # TODO(urgent): undo hack
            View._admin_view_hack(view)

            return {
                'pass': True,
                'message': 'View `%s` created.' % view.view_name,
                'data': view.view_name
            }

        return {
            'pass': False,
            'message': 'View `%s` could not be created.' % name
        }

    @staticmethod
    def _admin_view_hack(view):
        # admin user always needs to be added to every view
        # with Administrator group.

        admin_user = Hierarchy.get_user('admin')
        admin_group = Hierarchy.get_group(
            'Administrator',
            view.view_name
        )

        if admin_user:
            Hierarchy.toggle_user_from_view(
                admin_user,
                view,
            )

            Hierarchy.toggle_group_of_user(
                admin_group,
                admin_user,
                view
            )


class Group():

    @staticmethod
    def get(group_name=None, user_name=None, view_context=None):

        if(
            not group_name
            and not user_name
        ):

            return {
                'pass': False,
                'message': 'No group/user data provided.'
            }


        user = Hierarchy.get_user(user_name)
        if not user:
            return {
                'pass': False,
                'message': 'User `%s` was not found' % user_name
            }

        if not view_context:
            view_context = user.current_view

        if group_name:

            _group = Hierarchy.get_group(group_name, view_context)
            group = Group._group_presentation_hack(
                _group,
                view_context
            )
            return {
                'pass': True,
                'message': 'Group found.',
                'data': group
            }

        else:

            try:

                if view_context:

                    raw_groups = Hierarchy.get_groups_of_user(
                        user.user_name,
                        view_context
                    )

                    groups = []
                    for _group in raw_groups:
                        group = Group._group_presentation_hack(
                            _group,
                            view_context
                        )

                        groups.append(group)

                    return {
                        'pass': True,
                        'message': 'Groups found.',
                        'data': groups
                    }

            except Exception as e:

                logger.error('Unable to get group `%s`' % group_name)
                logger.exception(e)

        return {
            'pass': False,
            'message': 'Groups were not found for user {}.'.format(user_name)
        }

    @staticmethod
    def get_groups(view_context=None, user=None):

        if(
            not view_context
            and not user
        ):
            return {
                'pass': False,
                'message': 'A view context neither user was not provided.',
                'data': []
        }

        try:

            if not view_context:
                user = Hierarchy.get_user(user)
                view_context = user.current_view

            _groups = Hierarchy.get_groups_of_view(view_context)
            groups = []
            for _group in _groups:
                group = Group._group_presentation_hack(
                    _group,
                    view_context
                )

                if group:
                    groups.append(group)

            return {
                'pass': True,
                'message': 'Groups found.',
                'data': groups
            }

        except Exception as e:
            return {
                'pass': False,
                'message': 'Groups were not found for view %s.' % view_context,
                'data': []
            }

    @staticmethod
    def _group_presentation_hack(group, view_name):
        group_dict = group.dict()

        view = {'name': view_name}

        upg = Hierarchy.get_users_of_group(
            group.group_name,
            view_name
        )

        users = []
        for u in upg:
            users.append(
                {
                    "name": u.user_name
                }
            )

        group_dict[GroupKey.Users] = users
        group_dict[GroupKey.View] = view
        group_dict['name'] = group.group_name

        return group_dict

    @staticmethod
    def edit(**kwargs):

        data = {}

        group_name = kwargs.get('name', None)
        group_id = kwargs.get('id', None)
        user_name = kwargs.get('user_name', None)

        if (
            not group_name
            and not group_id
        ):

            return {
                'pass': False,
                'message': 'Group name/id was not provided.'
            }

        group = None
        user = Hierarchy.get_user(user_name)

        view_context = kwargs.get('view_context', None)
        if not view_context:
            view_context = user.current_view

        if group_id:

            group = Hierarchy.get_group_by_id(group_id)

        elif group_name and user_name:

            if user:
                group = Hierarchy.get_group(
                    group_name,
                    view_context
                )

        if group:

            data[GroupKey.View] = kwargs.get('view')
            data[GroupKey.Users] = kwargs.get('users')
            data[GroupKey.Permissions] = kwargs.get('permissions')

            if AdminUser in data[GroupKey.Users]:

                    message = 'The admin user has no editable properties.'
                    return {
                        'pass': False,
                        'message': message
                    }

            if (
                group.group_name == AdminGroup
                and data[GroupKey.Permissions]
            ):
                    return {
                        'pass': False,
                        'message': (
                            'Administrator has no editable permissions.'
                        )
                    }

            result = Hierarchy.edit_group(
                group.group_name,
                view_context,
                data
            )

            if result:

                return {
                    'pass': True,
                    'message': (
                        'Group `%s` has been updated.' % group.group_name
                    )
                }

        return {
            'pass': False,
            'message': (
                'Group `%s` could not be updated.' % (group_name or group_id)
            )
        }

    @staticmethod
    def delete(
        group_id=None,
        group_name=None,
        user_name=None,
        view_context=None
    ):

        if (
            not group_id
            or (group_name and user_name)
        ):

            return {
                'pass': False,
                'message': 'No group data provided.'
            }

        group = None
        if group_id:
            group = Hierarchy.get_group_by_id(group_id)

        else:
            user = Hierarchy.get_user(user_name)
            if user:

                if not view_context:
                    view_context = user.current_view

                group = Hierarchy.get_group(
                    group_name,
                    view_context
                )

        if group:

            if group.group_name in SafeGroups:
                return {
                    'pass': False,
                    'message': (
                        'Group `%s` cannot be deleted.' % group.group_name
                    )
                }

            result = Hierarchy.delete_group(
                group.group_name,
                group.view
            )

            if result:

                return {
                    'pass': True,
                    'message': 'Group `%s` was deleted.' % group.group_name
                }

        return {
            'pass': False,
            'message': (
                'Group `%s` could not be deleted.'
                % (group_id or group_name)
            )
        }

    @staticmethod
    def create(group_name=None, user_name=None, view_name=None):

        if not group_name:

            return {
                'pass': False,
                'message': 'Name for group not provided.'
            }

        if not view_name:
            view_name = get_current_view_name(user_name)

        if Hierarchy.get_group(group_name, view_name):
            return {
                'pass': False,
                'message': 'Group with this name and view already exist.'
            }

        group = Hierarchy.create_group(group_name, view_name=view_name)

        if group:

            if user_name:

                user = Hierarchy.get_user(user_name)

                if user:

                    Hierarchy.toggle_group_of_user(
                        user,
                        group,
                    )

            return {
                'pass': True,
                'message': 'Group `%s` created.' % group_name
            }

        return {
            'pass': False,
            'message': 'Group `%s` could not be created.' % group_name
        }

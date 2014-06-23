from vFense.core.view import View
from vFense.core.view._constants import DefaultViews
from vFense.core.view._db_model import ViewKeys
from vFense.core.user._db import (
    update_views_for_users, fetch_usernames,
    delete_all_users_from_view, delete_view_in_users
)
from vFense.core.user.users import validate_users
from vFense.core.group.groups import validate_groups

from vFense.core.group._db import (
    fetch_group_ids_for_view, delete_all_groups_from_view,
    delete_users_in_group_containing_view, delete_groups_from_view,
    add_views_to_groups
)

from vFense.core.view._db import (
    fetch_view, insert_view, update_children_for_view, delete_view,
    delete_users_in_view, update_view, update_usernames_for_view
)
from vFense.core.agent._db import (
    remove_all_agents_from_view, delete_all_agents_from_view,
    fetch_agent_ids_in_view, delete_hardware_for_agents,
    add_agents_to_views
)
from vFense.core.agent.agents import validate_agent_ids
from vFense.core.tag._db import (
    delete_agent_ids_from_all_tags, fetch_tag_ids,
    delete_tag_ids_from_view, delete_tag_ids_per_agent,
    delete_agent_ids_from_tags_in_view
)
from vFense.core.decorators import time_it
from vFense.errorz._constants import ApiResultKeys

from vFense.errorz.status_codes import (
    DbCodes, ViewCodes, GenericCodes, AgentCodes,
    ViewFailureCodes, AgentFailureCodes
)

class ViewManager(object):
    def __init__(self, name):
        self.name = name
        self.properties = self._view_properties()
        self.users = self.get_users()
        self.groups = self.get_groups()
        self.tags = self.get_tags()
        self.agents = self.get_agents()

    def _view_properties(self):
        """Retrieve view information.
        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> view_name = 'default'
            >>> view = ViewManager(view_name)
            >>> view._view_properties()

        Returns:
            Dictionary of view properties.
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            }
        """
        view_data = fetch_view(self.name)

        return view_data

    @time_it
    def get_attribute(self, view_attribute):
        """Retrieve view property.
        Args:
            view_attribute (str): The attribute you want to retrieve.
                example attributes.. users, download_package_url

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> view = ViewManager('global')
            >>> view.get_property('users')

        Return:
            String
        """
        view_data = fetch_view(self.name)
        view_key = None
        if view_data:
            view_key = view_data.get(view_attribute, None)

        return view_key

    def get_users(self):
        users = self.get_attribute(ViewKeys.Users)
        if not users:
            users = []
        return users

    def get_groups(self):
        groups = fetch_group_ids_for_view(self.name)
        return groups

    def get_agents(self):
        if self.name == DefaultViews.GLOBAL:
            agents = fetch_agent_ids_in_view()
        else:
            agents = fetch_agent_ids_in_view(self.name)
        return agents

    def get_tags(self):
        if self.name == DefaultViews.GLOBAL:
            tags = fetch_tag_ids()
        else:
            tags = fetch_tag_ids(self.name)
        return tags

    @time_it
    def create(self, view):
        """Create a new view inside of vFense

        Args:
            view (View): A view instance filled out with the
                appropriate fields.

        Kwargs:
            username (str): Name of the user that you are adding to this view.
                Default=None

        Basic Usage:
            >>> from vFense.core.view import View
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View(
                'global'
                package_download_url='https://10.0.0.15/packages/'
            )
            >>> manager = ViewManager(view.name)
            >>> manager.create(view)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                "data": [
                    {
                        "server_queue_ttl": 10,
                        "cpu_throttle": "normal",
                        "view_name": "global",
                        "ancestors": [],
                        "package_download_url_base": "https://10.0.0.15/packages/",
                        "agent_queue_ttl": 10,
                        "parent": null,
                        "net_throttle": 0,
                        "children": [],
                        "users": []
                    }
                ],
                "message": "create - view global created - ",
                "errors": [],
                "vfense_status_code": 14000,
                "generic_status_code": 1010
            }
        """
        view_exist = self.properties
        msg = ''
        results = {}
        invalid_fields = view.get_invalid_fields()
        results[ApiResultKeys.ERRORS] = invalid_fields

        if not invalid_fields and not view_exist:
            # Fill in any empty fields
            view.fill_in_defaults()
            parent_view = {}
            if view.name == DefaultViews.GLOBAL:
                view.parent = None
                view.ancestors = []
                view.children = []

            else:
                if not view.parent:
                    view.parent = DefaultViews.GLOBAL
                    view.ancestors = [view.parent]
                    parent_view = fetch_view(view.parent)

                else:
                    parent_view = fetch_view(view.parent)
                    if parent_view:
                        parent_view[ViewKeys.Children].append(view.name)
                        view.ancestors = parent_view[ViewKeys.Ancestors]
                        view.ancestors.append(view.parent)

            if not view.package_download_url:
                view.package_download_url = (
                    fetch_view(
                        DefaultViews.GLOBAL,
                        [ViewKeys.PackageUrl]
                    ).get(ViewKeys.PackageUrl)
                )

            usernames = list(set(fetch_usernames(True) + view.users))
            view.users = usernames
            object_status, _, _, generated_ids = (
                insert_view(view.to_dict())
            )

            if object_status == DbCodes.Inserted:
                generated_ids.append(view.name)
                msg = 'view %s created - ' % (view.name)
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectCreated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewCodes.ViewCreated
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = [view.to_dict()]

                if usernames:
                    update_views_for_users(
                        usernames, [view.name]
                    )
                if parent_view:
                    update_children_for_view(
                        parent_view[ViewKeys.ViewName], view.name
                    )

        elif view_exist:
            msg = 'view name %s already exists' % (view.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def add_users(self, users):
        """Add users to this view.

        Args:
            users (list): Add a list of users too this view.

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> users = ['foo', 'man', bar']
            >>> manager = ViewManager(view.name)
            >>> manager.add_users()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        users_exist = []
        if not isinstance(users, list):
            users = users.split()

        if set(users) == set(self.users):
            users_exist_in_view = True
            users_exist = list(set(users).intersection(self.users))

        elif set(users).issubset(self.users):
            users_exist_in_view = True
            users_exist = list(set(users).intersection(self.users))

        else:
            users_exist_in_view = False

        valid_users, _, invalid_users = validate_users(users)

        if view_exist:
            if users and valid_users and not users_exist_in_view:
                status_code, _, _, _ = (
                    update_usernames_for_view(users, self.name)
                )
                update_views_for_users(users, [self.name])
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following users: {0} were added to view {1}'
                        .format(', '.join(users), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsAddedToUser
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif users and invalid_users:
                msg = (
                    'Users {0} are not valid for this view {1}'
                    .format(', '.join(invalid_users), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            elif users and users_exist_in_view:
                msg = (
                    'Users {0} already exist in this view {1}'
                    .format(', '.join(users_exist), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Users do not exist in this view {0}'.format(self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View {0} does not exists'.format(self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def add_groups(self, groups):
        """Add groups to this view.

        Args:
            groups (list): List of group ids you want to add to this view.

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> groups = ['foo', 'man', bar']
            >>> manager = ViewManager(view.name)
            >>> manager.add_groups()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        groups_exist = []
        if not isinstance(groups, list):
            groups = groups.split()

        if set(groups) == set(self.groups):
            groups_exist_in_view = True
            groups_exist = list(set(groups).intersection(self.groups))

        elif set(groups).issubset(self.groups):
            groups_exist_in_view = True
            groups_exist = list(set(groups).intersection(self.groups))

        else:
            groups_exist_in_view = False

        valid_groups, _, invalid_groups = validate_groups(groups)

        if view_exist:
            if groups and valid_groups and not groups_exist_in_view:
                status_code, _, _, _ = (
                    add_views_to_groups(groups, [self.name])
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following groups: {0} were added to view {1}'
                        .format(', '.join(groups), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsAddedToGroup
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif groups and invalid_groups:
                msg = (
                    'Groups {0} are not valid for this view {1}'
                    .format(', '.join(invalid_groups), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            elif groups and groups_exist_in_view:
                msg = (
                    'Groups {0} already exist in this view {1}'
                    .format(', '.join(groups_exist), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Groups do not exist in this view {0}'.format(self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View {0} does not exists'.format(self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def remove_users(self, users=None):
        """Remove users from this view.

        Kwargs:
            users (list): Remove a list of users from this view.
                default=None (Remove all users from this view)

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.remove_users()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        if users:
            if not isinstance(users, list):
                users = users.split()
        else:
            users = self.users

        if set(users) == set(self.users):
            valid_users = True

        elif set(users).issubset(self.users):
            valid_users = True

        else:
            valid_users = False

        if view_exist:
            if users and valid_users:
                status_code, _, _, _ = delete_users_in_view(users, self.name)
                delete_view_in_users(self.name, users)
                delete_users_in_group_containing_view(users, self.name)
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following users: {0} were removed from view {1}'
                        .format(', '.join(users), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsRemovedFromUser
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif users and not valid_users:
                msg = (
                    'Users %s are not valid for this view %s'%
                    (', '.join(users), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Users do not exist in this view %s'% (self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def add_agents(self, agents):
        """Add agents from this view.

        Args:
            agents (list): Add a list of agente to this view.

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.add_agents()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        if not isinstance(agents, list):
            agents = agents.split()

        if view_exist:
            agents_are_valid, _, _ = validate_agent_ids(agents)
            if agents_are_valid:
                status_code, _, _, _ = (
                    add_agents_to_views(agents, [self.name])
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following agents: {0} were added to view {1}'
                        .format(', '.join(agents), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.AgentsAddedToView
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            else:
                msg = (
                    'Agents %s are not valid %s'%
                    (', '.join(agents), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureCodes.AgentsDoNotExist
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def move_agents(self, view_name, agents=None):
        """Move agents from this view to a new view.
        Args:
            view_name (str): Name ofthe view you are moving these agents too.
        Kwargs:
            agents (list): Move a list of agente from this view.
                default=None (Move all agents from this view)

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> new_view = 'Test 1'
            >>> manager.move_agents(new_view)

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        new_view_exist = fetch_view(view_name)
        if agents:
            if not isinstance(agents, list):
                agents = agents.split()
        else:
            agents = self.agents

        if set(agents) == set(self.agents):
            valid_agents = True

        elif set(agents).issubset(self.agents):
            valid_agents = True

        else:
            valid_agents = False

        if view_exist and self.name != DefaultViews.GLOBAL and new_view_exist:
            if agents and valid_agents:
                remove_all_agents_from_view(self.name, agents)
                delete_agent_ids_from_tags_in_view(agents, self.name)
                status_code, _, _, _ = (
                    add_agents_to_views(agents, [view_name])
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Agents: {0} were moved from view {1} to view {2}'
                        .format(', '.join(agents), self.name, view_name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.AgentsMovedToView
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif agents and not valid_agents and not new_view_exist:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        elif self.name == DefaultViews.GLOBAL:
            msg = 'Can not remove agents from the global view'
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.CantRemoveAgentsFromGlobalView
            )
            results[ApiResultKeys.MESSAGE] = msg

        elif not new_view_exist:
            msg = (
                'Agents can not move to a view that does not exist {0}'
                .format(view_name)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results


    @time_it
    def remove_agents(self, agents=None):
        """Remove agents from this view. This does not remove the agents
            from vFense, just from this view.

        Kwargs:
            agents (list): Remove a list of agente from this view.
                default=None (Remove all agents from this view)

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.remove_agents()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        if agents:
            if not isinstance(agents, list):
                agents = agents.split()
        else:
            agents = self.agents

        if set(agents) == set(self.agents):
            valid_agents = True

        elif set(agents).issubset(self.agents):
            valid_agents = True

        else:
            valid_agents = False

        if view_exist and self.name != DefaultViews.GLOBAL:
            if agents and valid_agents:
                status_code, _, _, _ = (
                    remove_all_agents_from_view(self.name, agents)
                )
                delete_agent_ids_from_tags_in_view(agents, self.name)
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following agents: {0} were removed from view {1}'
                        .format(', '.join(agents), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsRemovedFromAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif agents and not valid_agents:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        elif self.name == DefaultViews.GLOBAL:
            msg = 'Can not remove agents from the global view'
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.CantRemoveAgentsFromGlobalView
            )
            results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def delete_agents(self, agents=None):
        """Delete agents from this view and from inside of vFense.
            THIS WILL DELETE THE AGENTS FROM VFENSE

        Kwargs:
            agents (list): Remove a list of agente from this view.
                default=None (Remove all agents from this view)

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.delete_agents()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        if agents:
            if not isinstance(agents, list):
                agents = agents.split()
        else:
            agents = self.agents

        if set(agents) == set(self.agents):
            valid_agents = True

        elif set(agents).issubset(self.agents):
            valid_agents = True

        else:
            valid_agents = False

        if view_exist:
            if agents and valid_agents:
                status_code, _, _, _ = (
                    delete_all_agents_from_view(self.name, agents)
                )
                delete_agent_ids_from_all_tags(agents)
                delete_hardware_for_agents(agents)
                if status_code == DbCodes.Deleted:
                    msg = (
                        'The following agents: {0} were deleted from view {1}'
                        .format(', '.join(agents), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.AgentsDeleted
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif agents and not valid_agents:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results


    @time_it
    def remove_groups(self, groups=None):
        """Remove groups from this view.

        Kwargs:
            groups (list): Remove a list of groups from this view.
                default=None (Remove all groups from this view)

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.remove_users()

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}
        if groups:
            if not isinstance(groups, list):
                groups = groups.split()
        else:
            groups = self.groups

        if set(groups) == set(self.groups):
            valid_groups = True

        elif set(groups).issubset(self.groups):
            valid_groups = True

        else:
            valid_groups = False

        if view_exist:
            if groups and valid_groups:
                status_code, _, _, _ = (
                    delete_groups_from_view(groups, self.name)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'The following groups: {0} were removed from view {1}'
                        .format(', '.join(groups), self.name)
                    )

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsRemovedFromGroup
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.name]

            elif groups and not valid_groups:
                msg = (
                    'Groups %s are not valid for this view %s'%
                    (', '.join(groups), self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

            else:
                msg = (
                    'Groups do not exist in this view %s'% (self.name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.GroupsDoNotExistInThisView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results


    @time_it
    def remove(self, force=False):
        """Remove this view.

        Kwargs:
            force (boolean): Forcefully remove a view, even if users
                and groups exist.
                default=False

        Basic Usage:
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View('global')
            >>> manager = ViewManager(view.name)
            >>> manager.remove(view)

        Returns:
            Dictionary of the status of the operation.
            >>>
        """
        view_exist = self.properties
        msg = ''
        results = {}

        if view_exist:
            if not self.users and not self.groups and not force or force:
                object_status, _, _, generated_ids = (
                    delete_view(self.name)
                )

                if object_status == DbCodes.Deleted:
                    if force:
                        delete_all_users_from_view(self.name)
                        delete_all_groups_from_view(self.name)
                        self.remove_agents()
                        delete_tag_ids_per_agent(self.tags)
                        delete_tag_ids_from_view(self.name)
                        text = (
                            'View {view_name} deleted' +
                            'and all users: {users} and groups: {groups}' +
                            'were deleted'
                        )
                        msg = text.format(
                            **{
                                'view_name': self.name,
                                'users': self.users,
                                'groups': self.groups
                            }
                        )
                    else:
                        msg = 'View %s deleted - ' % (self.name)

                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewDeleted
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DELETED_IDS] = [self.name]

            else:
                msg = (
                    'Can not remove view %s, while users: %s'+'exist in view: %s'
                    % (self.name, self.users)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersExistForView
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results


    def edit_net_throttle(self, throttle):
        """Edit how much traffic the agent will use while downloading
            applications from vFense.

        Args:
            throttle (int): The number in kilobytes you want to throttle
                the download from the agent.

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_net_throttle(100)

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, net_throttle=throttle)
        results = self.__edit_properties(view)

        return results


    def edit_cpu_throttle(self, throttle):
        """Change how much CPU will be used while installing an application.

        Args:
            throttle (str): How much cpu the agent should use while
                installing an application. Valid throttle values..
                ("idle", "below_normal", "normal", "above_normal", "high")

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_cpu_throttle("normal")

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, cpu_throttle=throttle)
        results = self.__edit_properties(view)

        return results


    def edit_server_queue_ttl(self, ttl):
        """Change how long until an operation is considered expired
            on the vFense server.

        Args:
            ttl (int): Number of minutes until an operation is
                considered expired on the server.

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_server_queue_ttl(10)

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, server_queue_ttl=ttl)
        results = self.__edit_properties(view)

        return results


    def edit_agent_queue_ttl(self, ttl):
        """Change how long until an operation is considered expired
            on the vFense agent.

        Args:
            ttl (int): Number of minutes until an operation is
                considered expired on the agent.

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_agent_queue_ttl(10)

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, agent_queue_ttl=ttl)
        results = self.__edit_properties(view)

        return results


    def edit_download_url(self, url):
        """Change the url that the agent will use when downloadling
            applications from the vFense server.

        Args:
            url (str): The url that the agent will use while downloading
                from the vFense server. (https://ip_address/packages/"

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_download_url("https://10.0.0.100/packages/")

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, package_download_url=url)
        results = self.__edit_properties(view)

        return results


    def __edit_properties(self, view):
        """Edit the properties of a view.
        Args:
            view_data (dict): The fields you want to update.

        Basic Usage:
            >>> from vFense.view import View
            >>> from vFense.view.manager import ViewManager
            >>> view_name = 'global'
            >>> view = View(view_name, net_throttle=100)
            >>> manager = ViewManager(view.name)
            >>> manager.__edit_properties(view)

        Returns:
            Returns the results in a dictionary
        """
        view_exist = self.properties
        results = {}
        if view_exist:
            if isinstance(view, View):
                invalid_fields = view.get_invalid_fields()
                view_data = view.to_dict_non_null()
                view_data.pop(ViewKeys.ViewName, None)
                if not invalid_fields:
                    status_code, _, _, _ = (
                        update_view(self.name, view_data)
                    )
                    if status_code == DbCodes.Replaced:
                        msg = (
                            'view %s updated with data: %s'
                            % (self.name, view_data)
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            GenericCodes.ObjectUpdated
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            ViewCodes.ViewUpdated
                        )
                        results[ApiResultKeys.UPDATED_IDS] = [self.name]
                        results[ApiResultKeys.DATA] = [view_data]

                    if status_code == DbCodes.Unchanged:
                        msg = (
                            'View data: %s is the same as the previous values'
                            % (view_data)
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            GenericCodes.ObjectUnchanged
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            ViewCodes.ViewUnchanged
                        )
                        results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

                else:
                    msg = (
                        'View data: %s contains invalid_data'
                        % (self.name)
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUnchanged
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewFailureCodes.InvalidFields
                    )
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.name]
                    results[ApiResultKeys.ERRORS] = invalid_fields

            else:
                msg = (
                    'Argument must be an instance of View and not %s'
                    % (type(view))
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidValue
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.InvalidValue
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.name]

        else:
            msg = 'view %s does not exist' % (self.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewCodes.ViewUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.name]
            results[ApiResultKeys.INVALID_IDS] = [self.name]

        return results

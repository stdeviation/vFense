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
    add_views_to_groups, fetch_groupids, add_view_to_groups
)

from vFense.core.view._db import (
    fetch_view, insert_view, update_children_for_view, delete_view,
    delete_users_in_view, update_view, update_usernames_for_view,
    fetch_all_current_tokens, fetch_all_previous_tokens
)
from vFense.core.agent._db import (
    remove_all_agents_from_view, delete_all_agents_from_view,
    fetch_agent_ids_in_views, delete_hardware_for_agents,
    add_agents_to_views
)
from vFense.core.agent.agents import validate_agent_ids
from vFense.core.tag._db import (
    delete_agent_ids_from_all_tags, fetch_tag_ids,
    delete_tag_ids_from_view, delete_tag_ids_per_agent,
    delete_agent_ids_from_tags_in_view
)
from vFense.core.decorators import time_it
from vFense.core.results import ApiResults

from vFense.core.status_codes import (
    DbCodes, GenericCodes
)
from vFense.core.view.status_codes import (
    ViewCodes, ViewFailureCodes
)
from vFense.core.agent.status_codes import (
    AgentCodes, AgentFailureCodes
)
from vFense.utils.security import generate_token

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
            agents = fetch_agent_ids_in_views()
        else:
            agents = fetch_agent_ids_in_views([self.name])
        return agents

    def get_tags(self):
        if self.name == DefaultViews.GLOBAL:
            tags = fetch_tag_ids()
        else:
            tags = fetch_tag_ids(self.name)
        return tags

    def get_token(self):
        token = self.get_attribute(ViewKeys.Token)
        return token

    def get_previous_tokens(self):
        tokens = self.get_attribute(ViewKeys.PreviousTokens)
        if not tokens:
            tokens = []
        return tokens

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
        results = ApiResults()
        invalid_fields = view.get_invalid_fields()
        results.errors = invalid_fields

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
            groupids = list(set(fetch_groupids(True) + view.users))
            view.users = usernames
            view.groups = groupids
            view_data = view.to_dict()
            view_data[ViewKeys.Token] = self.generate_auth_token()
            object_status, _, _, generated_ids = (
                insert_view(view_data)
            )

            if object_status == DbCodes.Inserted:
                generated_ids.append(view.name)
                msg = 'view %s created - ' % (view.name)
                results.generic_status_code = (
                    GenericCodes.ObjectCreated
                )
                results.vfense_status_code = (
                    ViewCodes.ViewCreated
                )
                results.message = msg
                results.data = [view_data]

                if usernames:
                    update_views_for_users(
                        usernames, [view.name]
                    )

                if groupids:
                    add_view_to_groups(
                        groupids, view.name
                    )

                if parent_view:
                    update_children_for_view(
                        parent_view[ViewKeys.ViewName], view.name
                    )

        elif view_exist:
            msg = 'view name %s already exists' % (view.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewsAddedToUser
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif users and invalid_users:
                msg = (
                    'Users {0} are not valid for this view {1}'
                    .format(', '.join(invalid_users), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            elif users and users_exist_in_view:
                msg = (
                    'Users {0} already exist in this view {1}'
                    .format(', '.join(users_exist), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Users do not exist in this view {0}'.format(self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View {0} does not exists'.format(self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewsAddedToGroup
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif groups and invalid_groups:
                msg = (
                    'Groups {0} are not valid for this view {1}'
                    .format(', '.join(invalid_groups), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            elif groups and groups_exist_in_view:
                msg = (
                    'Groups {0} already exist in this view {1}'
                    .format(', '.join(groups_exist), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Groups do not exist in this view {0}'.format(self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View {0} does not exists'.format(self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewsRemovedFromUser
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif users and not valid_users:
                msg = (
                    'Users %s are not valid for this view %s'%
                    (', '.join(users), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Users do not exist in this view %s'% (self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.AgentsAddedToView
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            else:
                msg = (
                    'Agents %s are not valid %s'%
                    (', '.join(agents), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    AgentFailureCodes.AgentsDoNotExist
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.AgentsMovedToView
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif agents and not valid_agents and not new_view_exist:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        elif self.name == DefaultViews.GLOBAL:
            msg = 'Can not remove agents from the global view'
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.CantRemoveAgentsFromGlobalView
            )
            results.message = msg

        elif not new_view_exist:
            msg = (
                'Agents can not move to a view that does not exist {0}'
                .format(view_name)
            )
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results.message = msg

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewsRemovedFromAgent
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif agents and not valid_agents:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        elif self.name == DefaultViews.GLOBAL:
            msg = 'Can not remove agents from the global view'
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.CantRemoveAgentsFromGlobalView
            )
            results.message = msg

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewDoesNotExist
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        AgentCodes.AgentsDeleted
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif agents and not valid_agents:
                msg = (
                    'Agents %s are not valid for this view %s'%
                    (', '.join(agents), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Agents do not exist in this view %s'% (self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.AgentsDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()
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

                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewsRemovedFromGroup
                    )
                    results.message = msg
                    results.updated_ids = [self.name]

            elif groups and not valid_groups:
                msg = (
                    'Groups %s are not valid for this view %s'%
                    (', '.join(groups), self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

            else:
                msg = (
                    'Groups do not exist in this view %s'% (self.name)
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.GroupsDoNotExistInThisView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        results = ApiResults()

        if view_exist:
            if not self.users and not self.groups and not force or force:
                object_status, _, _, generated_ids = (
                    delete_view(self.name)
                )

                if object_status == DbCodes.Deleted:
                    if force:
                        if self.users:
                            delete_all_users_from_view(self.name)
                        if self.groups:
                            delete_all_groups_from_view(self.name)
                        if self.agents:
                            self.remove_agents()
                        if self.tags:
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

                    results.generic_status_code = (
                        GenericCodes.ObjectDeleted
                    )
                    results.vfense_status_code = (
                        ViewCodes.ViewDeleted
                    )
                    results.message = msg
                    results.deleted_ids = [self.name]

            else:
                msg = (
                    'Can not remove view %s, while users: %s'
                    % (self.name, ', '.join(self.users))
                )
                results.generic_status_code = (
                    GenericCodes.ObjectUnchanged
                )
                results.vfense_status_code = (
                    ViewFailureCodes.UsersExistForView
                )
                results.message = msg
                results.unchanged_ids = [self.name]

        else:
            msg = 'View %s does not exists' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectExists
            )
            results.vfense_status_code = (
                ViewFailureCodes.ViewExists
            )
            results.message = msg

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
        """Change the url that the agent will use when downloading
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

    def edit_time_zone(self, time_zone):
        """Change the time zone that the schedule will use when running.

        Args:
            time_zone (str): The time_zone vFense will use when running
                scheduled jobs. Example (UTC, US/Eastern, Europe/London)

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.edit_time_zone("US/Eastern")

        Returns:
            Returns the results in a dictionary
        """
        view = View(self.name, time_zone=time_zone)
        results = self.__edit_properties(view)

        return results

    def update_token(self):
        """Update the auth token for this view.

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.update_token()

        Returns:
            Returns the results in a dictionary
        """
        token = self.generate_auth_token()
        current_token = self.get_token()
        previous_tokens = self.get_previous_tokens()
        if current_token:
            previous_tokens = (
                list(set(previous_tokens).union([current_token]))
            )
        view = View(self.name, token=token, previous_tokens=previous_tokens)
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
        results = ApiResults()
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
                        results.message = msg
                        results.generic_status_code = (
                            GenericCodes.ObjectUpdated
                        )
                        results.vfense_status_code = (
                            ViewCodes.ViewUpdated
                        )
                        results.updated_ids = [self.name]
                        results.data = [view_data]

                    if status_code == DbCodes.Unchanged:
                        msg = (
                            'View data: %s is the same as the previous values'
                            % (view_data)
                        )
                        results.message = msg
                        results.generic_status_code = (
                            GenericCodes.ObjectUnchanged
                        )
                        results.vfense_status_code = (
                            ViewCodes.ViewUnchanged
                        )
                        results.unchanged_ids = [self.name]

                else:
                    msg = (
                        'View data: %s contains invalid_data'
                        % (self.name)
                    )
                    results.message = msg
                    results.generic_status_code = (
                        GenericCodes.ObjectUnchanged
                    )
                    results.vfense_status_code = (
                        ViewFailureCodes.InvalidFields
                    )
                    results.unchanged_ids = [self.name]
                    results.errors = invalid_fields

            else:
                msg = (
                    'Argument must be an instance of View and not %s'
                    % (type(view))
                )
                results.message = msg
                results.generic_status_code = (
                    GenericCodes.InvalidValue
                )
                results.vfense_status_code = (
                    ViewFailureCodes.InvalidValue
                )
                results.unchanged_ids = [self.name]

        else:
            msg = 'view %s does not exist' % (self.name)
            results.generic_status_code = (
                GenericCodes.ObjectUnchanged
            )
            results.vfense_status_code = (
                ViewCodes.ViewUnchanged
            )
            results.message = msg
            results.unchanged_ids = [self.name]
            results[ApiResultKeys.INVALID_IDS] = [self.name]

        return results

    def generate_auth_token(self):
        """Generate a new token for this view.

        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> manager = ViewManager("global")
            >>> manager.generate_auth_token()

        Returns:
            Returns the results in a dictionary
        """
        new_token = generate_token()
        current_tokens = fetch_all_current_tokens()
        previous_tokens = fetch_all_previous_tokens()
        while (new_token in current_tokens or new_token in previous_tokens):
            new_token = generate_token()

        return new_token


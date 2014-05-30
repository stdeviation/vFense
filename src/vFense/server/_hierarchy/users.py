from vFense.server.hierarchy import *


class User():
    """Represents a User.

    Attributes:

        username: Name (string) of the User.

        full_name: Full name for the User.

        id: For a User id == name. Used to determine if it exist in DB.

        password: User's password.

        email: Email of the user.

        enabled: A boolean indicating if the User is enabled. That is able to
            log in.
    """

    def __init__(self, name=None, full_name=None, email=None, password='',
                 groups=None, views=None, default_view=None,
                 current_view=None, enabled=True):

        self.name = name
        self.full_name = full_name
        self.password = password
        self.email = email
        self.enabled = enabled

        self.id = None

        self._views = []
        self._raw_views = []

        self._current_view = None
        self._raw_current_view = {}

        self._default_view = None
        self._raw_default_view = {}

        self._groups = []
        self._raw_groups = []

        if groups:
            for g in groups:
                self.add_group(g)

        if views:
            for c in views:
                self.add_view(c)

        if default_view:
            self.set_default_view(default_view)

        if current_view:
            self.set_current_view(current_view)

    def add_group(self, group):
        """Adds group to User.

        Adds the group to the User's list of groups. Doesn't touch the
        Groups collection though.

        Args:

            group: A Group instance.

        Returns:

            Nothing
        """

        g = {UserKey.Name: group.name, UserKey.Id: group.id}
        gi = GroupInfo(group.id, group.name)

        self._raw_groups.append(g)
        self._groups.append(gi)

    def remove_group(self, group):
        """Removes a group from the User.

        Removes the group to the User's list of groups. Doesn't touch the
        Groups collection though.

        Args:

            group: A Group instance.

        Returns:

            True if group was removed successfully, False otherwise.
        """

        g = {UserKey.Name: group.name, UserKey.Id: group.id}
        gi = GroupInfo(group.id, group.name)

        self._raw_groups.remove(g)
        self._groups.remove(gi)

    def add_view(self, view):
        """Adds a view to the User.

        Args:

            view: A View instance.

        Returns:

            True if user was added successfully, False otherwise.
        """

        c = {UserKey.Name: view.name}
        ci = ViewInfo(view.name)

        self._raw_views.append(c)
        self._views.append(ci)

    def remove_view(self, view):
        """Removes a view from the User.

        Args:

            view: A View instance.

        Returns:

            True if user was removed successfully, False otherwise.
        """

        c = {UserKey.Name: view.name}
        ci = ViewInfo(view.name)

        self._raw_views.remove(c)
        self._views.remove(ci)

    def set_current_view(self, view):
        """Sets the currently selected view of the User.

        The view must be part of the User's list of views to be the
        'current view'.

        Args:

            view: A View instance.

        Returns:

            True if user was removed successfully, False otherwise.
        """

        c = {UserKey.Name: view.name}
        ci = ViewInfo(view.name)

        self._raw_current_view = c
        self._current_view = ci

    def set_default_view(self, view):
        """Sets the default view of the User.

        The view must be part of the User's list of views to be the
        'default view'.

        Args:

            view: A View instance.

        Returns:

            True if user was removed successfully, False otherwise.
        """

        c = {UserKey.Name: view.name}
        ci = ViewInfo(view.name)

        self._raw_default_view = c
        self._default_view = ci

    def get_current_view(self, raw=False):
        """Returns the current view the User has access to.
        """

        if raw:

            return self._raw_current_view

        return self._current_view

    def get_default_view(self, raw=False):
        """Returns the default view the User has access to.
        """

        if raw:

            return self._raw_current_view

        return self._default_view

    def get_views(self, raw=False):
        """Returns the views the User has access to.
        """

        if raw:

            return self._raw_views

        return self._views

    def get_groups(self, raw=False):
        """Returns the groups the User has access to.
        """

        if raw:

            return self._raw_groups

        return self._groups

    def to_safe_dict(self):
        """
        """

        _user = {}

        _user['username'] = self.name
        _user['full_name'] = self.full_name
        _user['email'] = self.email
        _user['current_view'] = self.get_current_view(raw=True)
        _user['default_view'] = self.get_default_view(raw=True)
        _user['views'] = self.get_views(raw=True)
        _user['groups'] = self.get_groups(raw=True)

        return _user

    def __repr__(self):

        return (
            'User(name=%r, groups=%r)' %
            (self.name, self.get_groups(raw=True))
        )

    def __eq__(self, other):

        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

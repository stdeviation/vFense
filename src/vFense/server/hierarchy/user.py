from vFense.server.hierarchy import UserKey, DefaultView


class User():

    def __init__(
        self, user_name, password, full_name, email,
        current_view=DefaultView, default_view=DefaultView,
        enabled=True
    ):

        self.user_name = user_name
        self.password = password
        self.full_name = full_name
        self.email = email
        self.enabled = enabled

        self.current_view = current_view
        self.default_view = default_view

    def dict(self):

        return {
            UserKey.UserName: self.user_name,
            UserKey.FullName: self.full_name,
            UserKey.Email: self.email,
            UserKey.Enabled: self.enabled,
            UserKey.CurrentView: self.current_view,
            UserKey.DefaultView: self.default_view
        }

    @staticmethod
    def from_dict(user):

        u = User(
            user.get(UserKey.UserName),
            user.get(UserKey.Password),
            user.get(UserKey.FullName),
            user.get(UserKey.Email),
            user.get(UserKey.CurrentView),
            user.get(UserKey.DefaultView),
            user.get(UserKey.Enabled)
        )

        return u

    def __repr__(self):

        return (
            "User(name=%r, fullname=%r, email=%r)"
            % (self.user_name, self.full_name, self.email)
        )

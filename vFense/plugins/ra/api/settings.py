import json

from vFense.core.api.base import BaseHandler

from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager

from vFense.plugins.ra import ra_settings


class SetPassword(BaseHandler):

    def post(self):

        current_user = self.get_current_user()
        view_name = (
            UserManager(current_user).get_attribute(UserKeys.CurrentView)
        )
        body = json.loads(self.request.body)
        password = body.get('password')

        results = ra_settings.save_rd_password(
            password=password,
            user=current_user,
            view=current_view
        )

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

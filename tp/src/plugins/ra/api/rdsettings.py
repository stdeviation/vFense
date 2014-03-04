import json

from vFense.server.handlers import BaseHandler

from vFense.plugins import ra
from vFense.plugins.ra import creator


class RDPassword(BaseHandler):

    def post(self, agent_id=None):

        current_user = self.get_current_user()
        body = json.loads(self.request.body)
        password = body.get('password')

        results = creator.save_rd_password(
            password=password,
            user=current_user
        )

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

from ast import literal_eval
import tornado.web


class AgentBaseHandler(tornado.web.RequestHandler):

    def get_token(self):
        try:
            auth_headers = (
                literal_eval(self.request.headers.get('Authentication'))
            )
            token = auth_headers.get('token')
            return token

        except Exception:
            return None

    def get_agent_id(self):
        try:
            auth_headers = (
                literal_eval(self.request.headers.get('Authentication'))
            )
            agent_id = auth_headers.get('agent_id')
            return agent_id

        except Exception:
            return None

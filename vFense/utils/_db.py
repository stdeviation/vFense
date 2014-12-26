from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys,
)
from vFense.core.decorators import time_it, catch_it
from vFense.db.client import db_create_close, r


@time_it
@catch_it(None)
@db_create_close
def get_oscode_by_osstring(os_string, conn=None):
    os_code = list(
        r
        .table(AgentCollections.Agents)
        .filter(
            lambda x: x[AgentKeys.OsString].match(os_string)
        )
        .map(lambda x: x[AgentKeys.OsCode])
        .distinct()
        .run(conn)
    )
    if os_code:
        return os_code[0]
    else:
        os_code = None

    return os_code

from vFense.db.client import r
from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys,
    TagsPerAgentIndexes, TagKeys
)

from vFense.core.agent._db_model import (
    AgentKeys
)

class Merge():
    TAGS = (
        {
            TagCollections.Tags: (
                r
                .table(TagCollections.TagsPerAgent)
                .get_all(
                    r.row[TagsPerAgentKeys.AgentId],
                    index=TagsPerAgentIndexes.AgentId
                )
                .eq_join(
                    TagKeys.TagId,
                    r.table(TagCollections.Tags)
                )
                .zip()
                .pluck(
                    TagsPerAgentKeys.TagId,
                    TagsPerAgentKeys.TagName
                )
                .coerce_to('array')
            )
        }
    )
    AGENTS = (
        lambda x:
        {
            AgentKeys.LastAgentUpdate: (
                x[AgentKeys.LastAgentUpdate].to_epoch_time()
            )
        }
    )

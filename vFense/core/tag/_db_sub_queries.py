from vFense.db.client import r
from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys,
    TagsPerAgentIndexes, TagMappedKeys, TagKeys
)

from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections
)
class TagMerge():
    AGENTS = (
        {
            TagMappedKeys.Agents: (
                r
                .table(TagCollections.TagsPerAgent)
                .get_all(
                    r.row[TagsPerAgentKeys.TagId],
                    index=TagsPerAgentIndexes.TagId
                )
                .pluck(
                    TagsPerAgentKeys.AgentId,
                )
                .eq_join(
                    TagsPerAgentKeys.AgentId,
                    r.table(AgentCollections.Agents)
                )
                .map(
                    lambda y:
                    {
                        AgentKeys.AgentId: (
                            y['right'][AgentKeys.AgentId]
                        ),
                        AgentKeys.ComputerName: (
                            y['right'][AgentKeys.ComputerName]
                        ),
                        AgentKeys.DisplayName: (
                            y['right'][AgentKeys.DisplayName]
                        ),
                        AgentKeys.Views: (
                            y['right'][AgentKeys.Views]
                        ),
                    }
                )
                .coerce_to('array')
            )
        }
    )

    TAGS = (
        {
            TagKeys.DateModified: (
                r.row[TagKeys.DateModified].to_epoch_time()
            ),
            TagKeys.DateAdded: (
                r.row[TagKeys.DateAdded].to_epoch_time()
            )
        }
    )

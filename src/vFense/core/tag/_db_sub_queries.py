from vFense.db.client import r
from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys,
    TagsPerAgentIndexes, TagMappedKeys
)

from vFense.core.agent._db_model import (
    AgentKeys
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
                    index=TagsPerAgentIndexes.AgentId
                )
                .map(
                    lambda y:
                    {
                        AgentKeys.AgentId: (
                            y['left'][AgentKeys.AgentId]
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

from vFense.db.client import r
from vFense.core.tag import TagCollections, TagsPerAgentKey, \
    TagsPerAgentIndexes, TagsKey

class Merge():
    TAGS = (
        {
            TagCollections.Tags: (
                r
                .table(TagCollections.TagsPerAgent)
                .get_all(
                    r.row[TagsPerAgentKey.AgentId],
                    index=TagsPerAgentIndexes.AgentId
                )
                .eq_join(
                    TagsKey.TagId,
                    r.table(TagCollections.Tags)
                )
                .zip()
                .pluck(
                    TagsPerAgentKey.TagId,
                    TagsPerAgentKey.TagName
                )
                .coerce_to('array')
            )
        }
    )


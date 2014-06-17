class TagCollections():
    Tags = 'tags'
    TagsPerAgent = 'tag_per_agent'


class TagKeys():
    TagId = 'tag_id'
    TagName = 'tag_name'
    AgentIds = 'agent_ids'
    ViewName = 'view_name'
    Global = 'global'
    ProductionLevel = 'production_level'

class TagsPerAgentKey():
    Id = 'id'
    TagId = 'tag_id'
    TagName = 'tag_name'
    AgentId = 'agent_id'
    ViewName = 'view_name'

class TagsIndexes():
    ViewName = 'view_name'
    TagNameAndView = 'by_tagname_and_view'

class TagsPerAgentIndexes():
    AgentId = 'agent_id'
    TagId = 'tag_id'
    ViewName = 'view_name'
    AgentIdAndTagId = 'agent_id_and_tag_id'

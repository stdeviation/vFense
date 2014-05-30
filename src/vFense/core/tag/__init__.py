TagsCollection = 'tags'
TagsPerAgentCollection = 'tag_per_agent'

class TagCollections():
    Tags = 'tags'
    TagsPerAgent = 'tag_per_agent'


class TagsKey():
    TagId = 'tag_id'
    TagName = 'tag_name'
    ViewName = 'view_name'
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

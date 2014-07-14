from vFense.core.tag._db_model import TagKeys, TagMappedKeys
from vFense.core.tag._constants import (
    TagDefaults
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Tag(object):
    """Used to represent an instance of a tag."""

    def __init__(self, tag_name=None, environment=None,
                 view_name=None, is_global=None, agents=None
                 ):
        """
        Kwargs:
            tag_name (str): The name of the tag
            environment (str): User defined environment.
            view_name (str): The name of the view, this tag belongs too.
            is_global (bool): If this tag is a global tag. A global tag,
                is a tag that allows agents from any view to be a
                part of this tag.
        """
        self.tag_name = tag_name
        self.environment = environment
        self.view_name = view_name
        self.is_global = is_global
        self.agents = agents


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new tag instance and only want to fill
            in a few fields, then allow the add tag functions to call this
            method to fill in the rest.
        """

        if not self.environment:
            self.environment = TagDefaults.ENVIRONMENT

        if not self.is_global:
            self.is_global = TagDefaults.IS_GLOBAL

        if self.is_global and not self.view_name:
            self.view_name = TagDefaults.VIEW_NAME

        if not self.agents:
            self.agents = TagDefaults.AGENTS

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        TagKeys.Global: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.tag_name:
            if not isinstance(self.tag_name, basestring):
                invalid_fields.append(
                    {
                        TagKeys.TagName: self.tag_name,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.view_name:
            if not isinstance(self.view_name, basestring):
                invalid_fields.append(
                    {
                        TagKeys.ViewName: self.view_name,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.environment:
            if not isinstance(self.environment, basestring):
                invalid_fields.append(
                    {
                        TagKeys.Environment: self.environment,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.agents:
            if not isinstance(self.agents, list):
                invalid_fields.append(
                    {
                        TagMappedKeys.Agents: self.agents,
                        CommonKeys.REASON: 'Must be a list',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                view.

                Ex:
                {
                    "agent_queue_ttl": 100 ,
                    "cpu_throttle":  "high" ,
                    "view_name":  "default" ,
                    "net_throttle": 100 ,
                    "package_download_url_base": https://192.168.8.14/packages/,
                    "server_queue_ttl": 100
                }

        """

        return {
            TagKeys.Environment: self.environment,
            TagKeys.TagName: self.tag_name,
            TagKeys.ViewName: self.view_name,
            TagKeys.Global: self.is_global,
            TagMappedKeys.Agents: self.agents,
        }

    def to_dict_non_null(self):
        """ Use to get non None fields of a tag. Useful when
        filling out just a few fields to update the tag in the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        tag_dict = self.to_dict()

        return {k:tag_dict[k] for k in tag_dict
                if tag_dict[k] != None}

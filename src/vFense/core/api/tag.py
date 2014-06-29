import simplejson as json

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.view._constants import DefaultViews
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.errorz.error_messages import GenericResults
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    GenericCodes, TagCodes, TagFailureCodes, GenericFailureCodes
)
from vFense.core.agent._constants import ProductionLevels
from vFense.core.tag._db_model import TagKeys
from vFense.core.tag import Tag
from vFense.core.tag.manager import TagManager
from vFense.core.tag.search.search import RetrieveTags
from vFense.core._constants import DefaultQueryValues, SortValues
from vFense.core.api._constants  import (
    ApiArguments, TagApiArguments, ApiValues
)
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message
)
from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager
from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)
from vFense.core.agent.operations.store_agent_operations import (
    StoreAgentOperations
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class TagsHandler(BaseHandler):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        try:
            query = self.get_argument(ApiArguments.QUERY, None)
            count = int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
            offset = int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
            sort = (
                self.get_argument(
                    ApiArguments.SORT, DefaultQueryValues.SORT
                )
            )
            sort_by = (
                self.get_argument(ApiArguments.SORT_BY, TagKeys.TagName)
            )
            prod_level = (
                self.get_argument(TagApiArguments.PRODUCTION_LEVEL, None)
            )
            search = (
                RetrieveTags(active_view, count, offset, sort, sort_by)
            )
            if not query and not prod_level:
                results = self.get_all_tags(search)

            elif query and not prod_level:
                results = self.get_all_tags_by_name(search, query)

            elif prod_level and not query:
                results = self.get_all_tags_by_prod_level(search, prod_level)

            elif query and prod_level:
                results = (
                    self.get_all_tags_by_prod_level_and_regex(
                        search, prod_level, query
                    )
                )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('Get Tags', 'Tags', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_all_tags(self, search):
        results = search.all()
        return results

    @results_message
    def get_all_tags_by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    def get_all_tags_by_prod_level(self, search, prod_level):
        results = (
            search.by_key_val(search, TagKeys.ProductionLevel, prod_level)
        )
        return results

    @results_message
    def get_all_tags_by_prod_level_and_regex(self, search, prod_level, regex):
        results = (
            search.by_key_val_and_query(
                search, TagKeys.ProductionLevel, prod_level, regex
            )
        )
        return results

    @convert_json_to_arguments
    @authenticated_request
    @check_permissions(Permissions.CREATE_TAG)
    def post(self):
        username = self.get_current_user()
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            tag_name = self.arguments.get(TagApiArguments.TAG_NAME)
            prod_level = (
                self.arguments.get(
                    TagApiArguments.PRODUCTION_LEVEL,
                    ProductionLevels.PRODUCTION
                )
            )
            if active_view == DefaultViews.GLOBAL:
                is_global = True
            else:
                is_global = False

            tag = Tag(tag_name, prod_level, active_view, is_global)
            results = self.create_tag(tag)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('Create Tag', 'Tags', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def create_tag(self, tag):
        manager = TagManager()
        results = manager.create(tag)
        return results

    @convert_json_to_arguments
    @authenticated_request
    @check_permissions(Permissions.REMOVE_TAG)
    def delete(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            tag_ids = self.arguments.get(TagApiArguments.TAG_IDS)
            results = self.remove_tags(tag_ids)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('agentids and tag_id', 'delete agents_in_tagid', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @log_operation(AdminActions.REMOVE_TAGS, vFenseObjects.TAG)
    def remove_tags(self, tags):
        if not isinstance(tags, list):
            tags = tags.split()
        end_results = {}
        tags_deleted = []
        tags_unchanged = []
        for tag_id in tags:
            manager = TagManager(tag_id)
            results = manager.remove()
            if (results[ApiResultKeys.VFENSE_STATUS_CODE]
                    == TagCodes.TagsDeleted):
                tags_deleted.append(tag_id)
            else:
                tags_unchanged.append(tag_id)

        end_results[ApiResultKeys.UNCHANGED_IDS] = tags_unchanged
        end_results[ApiResultKeys.DELETED_IDS] = tags_deleted

        if tags_deleted and tags_unchanged:
            msg = (
                'Tags: {0} deleted and these tags didnt: {1}'
                .format(
                    ', '.join(tags_deleted),
                    ', '.join(tags_unchanged),
                )
            )
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.FailedToDeleteAllObjects
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                TagFailureCodes.FailedToDeleteTags
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        elif tags_deleted and not tags_unchanged:
            msg = (
                'Tags: {0} deleted.'.format(', '.join(tags))
            )
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectsDeleted
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                TagCodes.TagsDeleted
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        elif tags_unchanged and not tags_deleted:
            msg = (
                'Tags: {0} failed to delete: {1}'
                .format(', '.join(tags), ', '.join(tags_unchanged))
            )
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectsUnchanged
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                TagFailureCodes.FailedToDeleteTags
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        return end_results

class TagHandler(BaseHandler):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self, tag_id):
        username = self.get_current_user()
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        search = RetrieveTags(active_view)
        results = self.get_tag(search, tag_id)
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def get_tag(self, search, tag_id):
        results = search.by_id(tag_id)
        return results


    @authenticated_request
    @convert_json_to_arguments
    def post(self, tag_id):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            reboot = self.arguments.get(TagApiArguments.REBOOT, None)
            shutdown = self.arguments.get(TagApiArguments.SHUTDOWN, None)
            apps_refresh = (
                self.arguments.get(TagApiArguments.APPS_REFRESH, None)
            )
            operation = (
                StoreAgentOperations(
                    username, view_name, uri, method
                )
            )
            if reboot:
                results = (
                    self.reboot(operation, tag_id)
                )
            elif shutdown:
                results = self.shutdown(operation, tag_id)

            elif apps_refresh:
                results = self.apps_refresh(operation, tag_id)

            else:
                results = (
                    GenericResults(
                        username, uri, method
                    ).incorrect_arguments()
                )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke(tag_id, '', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.REBOOT)
    def reboot(self, operation, tag_id):
        results = operation.reboot(tag_id=tag_id)
        return results

    @results_message
    @check_permissions(Permissions.SHUTDOWN)
    def shutdown(self, operation, tag_id):
        results = operation.shutdown(tag_id=tag_id)
        return results

    def apps_refresh(self, operation, tag_id):
        results = operation.apps_refresh(tag_id=tag_id)
        return results


    @convert_json_to_arguments
    @authenticated_request
    def put(self, tag_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            agent_ids = self.arguments.get('agent_ids')
            action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)
            manager = TagManager(tag_id)
            if action == ApiValues.ADD:
                results = self.add_agents_to_tag(manager, agent_ids)
            elif action == ApiValues.DELETE:
                results = self.remove_agents_from_tag(manager, agent_ids)
            else:
                results = (
                    GenericResults(
                        username, uri, method
                    ).incorrect_arguments()
                )
            print results
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke(tag_id, '', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADD_AGENTS_TO_TAG)
    def add_agents_to_tag(self, manager, agent_ids):
        if not isinstance(agent_ids, list):
            agent_ids = agent_ids.split()
        results = manager.add_agents(agent_ids)
        print results
        return results

    @results_message
    @check_permissions(Permissions.REMOVE_AGENTS_FROM_TAG)
    def remove_agents_from_tag(self, manager, agent_ids):
        if not isinstance(agent_ids, list):
            agent_ids = agent_ids.split()
        results = manager.remove_agents(agent_ids)
        return results

    @convert_json_to_arguments
    @authenticated_request
    def delete(self, tag_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            manager = TagManager(tag_id)
            results = self.remove_tag(manager)
            print results
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke(tag_id, '', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.REMOVE_TAG)
    def remove_tag(self, manager):
        results = manager.remove()
        return results

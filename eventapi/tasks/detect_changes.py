import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

from typing import Set, Dict, Callable, Tuple, List

from eventapi.helpers.stream_redis import stream_events_to_redis
from eventapi.helpers.helpers import get_date_from_concat_str, get_frequency_by_value, get_license_name_by_value

log = logging.getLogger(__name__)

EVENT_TYPE_DATASET_CREATED = 'dataset-created'
EVENT_TYPE_DATASET_DELETED = 'dataset-deleted'
EVENT_TYPE_DATASET_METADATA_CHANGED = 'dataset-metadata-changed'

EVENT_TYPE_RESOURCE_DELETED = 'resource-deleted'
EVENT_TYPE_RESOURCE_CREATED = 'resource-created'
EVENT_TYPE_RESOURCE_DATA_CHANGED = 'resource-data-changed'
EVENT_TYPE_RESOURCE_METADATA_CHANGED = 'resource-metadata-changed'

# Fields for file structure_change: num_sheets, num_rows, num_cols, has_merged_cells, header, hxl_header
EVENT_TYPE_SPREADSHEET_SHEET_CREATED = 'spreadsheet-sheet-created'
EVENT_TYPE_SPREADSHEET_SHEET_DELETED = 'spreadsheet-sheet-deleted'
EVENT_TYPE_SPREADSHEET_SHEET_CHANGED = 'spreadsheet-sheet-changed'

_VOCABULARY_ID = 'b891512e-9516-4bf5-962a-7a289772a2a1'

DATASET_FIELDS = {'name', 'title', 'notes', 'subnational', 'dataset_source', 'owner_org', 'dataset_date',
                  'data_update_frequency', 'data_update_frequency', 'license_id', 'license_other', 'methodology',
                  'maintainer', 'methodology_other', 'caveats', 'archived',
                  'private', 'is_requestdata_type', 'dataset_preview', 'state'}
RESOURCE_FIELDS = {'name', 'format', 'description', 'microdata', 'resource_type', 'url'}
SPREADSHEET_FIELDS = {'nrows', 'ncols', 'header_hash', 'hashtag_hash', 'hxl_header_hash', 'name', 'has_merged_cells'}


@dataclass
class Event(object):
    event_type: str
    event_time: str
    event_source: str
    # initiator_user_id: str
    initiator_user_name: str
    org_id: str
    org_name: str


@dataclass
class DatasetEvent(Event):
    dataset_name: str
    dataset_id: str
    changed_fields: [dict]


@dataclass
class ResourceEvent(DatasetEvent):
    resource_name: str
    resource_id: str


@dataclass
class FileStructureEvent(ResourceEvent):
    sheet_id: str


def detect_changes(task_arguments) -> List[Event]:
    '''
    :param task_arguments: should contain at least: username, old_dataset_dict, new_dataset_dict,
     Also mixpanel_token depends on the flag send_mixpanel
    :type task_arguments: dict
    '''
    username = task_arguments['username']
    old_dataset_dict = task_arguments['old_dataset_dict']
    new_dataset_dict = task_arguments['new_dataset_dict']

    detector = DatasetChangeDetector(username, old_dataset_dict, new_dataset_dict)
    detector.detect_changes()
    for event in detector.change_events:
        log.info('Event: {}'.format(event))

    event_list = [asdict(e) for e in detector.change_events]
    if event_list:
        try:
            log.info(json.dumps(event_list, indent=4))
            stream_events_to_redis(event_list)
            # stream_events_to_eventbridge(event_list)
        except Exception as e:
            log.error(str(e))

    return detector.change_events


#     post_changes(event_list)
#
#
# def post_changes(event_list: [dict]):
#     import requests
#     import json
#     url = 'http://gislayer:5000/api/send-events'
#     response = requests.post(url, data=json.dumps(event_list), headers={'Content-type': 'application/json'})
#     pass


class DatasetChangeDetector(object):

    def __init__(self, username: str, old_dataset_dict: dict, new_dataset_dict: dict) -> None:
        super().__init__()
        self.change_events: [Event] = []
        self.timestamp = datetime.utcnow().isoformat()
        self.username = username
        self.org_id = new_dataset_dict.get('organization', {}).get('id')
        self.org_name = new_dataset_dict.get('organization', {}).get('name')
        self.old_dataset_dict = old_dataset_dict
        self.new_dataset_dict = new_dataset_dict
        self.package_type = new_dataset_dict['type'] if new_dataset_dict else old_dataset_dict['type']

        if self.package_type == 'dataset':
            self.dataset_id = new_dataset_dict['id']
            self.dataset_name = new_dataset_dict['name']

            self._replace_needed_values()

            self.created_resource_ids, self.deleted_resource_ids, self.new_resources_map, self.old_resources_map = \
                _compare_lists(old_dataset_dict.get('resources', []), new_dataset_dict.get('resources', []),
                               lambda idx, resource_dict: resource_dict['id'])

            self.old_resources_map = {r['id']: r for r in old_dataset_dict.get('resources', [])}
            self.new_resources_map = {r['id']: r for r in new_dataset_dict.get('resources', [])}

            self.common_resource_ids = set(self.old_resources_map.keys()).intersection(self.new_resources_map.keys())

    def detect_changes(self):
        if self.package_type == 'dataset':
            self._detect_created_dataset()
            self._detect_deleted_dataset()
            self._detect_metadata_changed_dataset()
            self._detect_deleted_resources()
            self._detect_created_resources()
            self._detect_changed_resources()

    def create_event_dict(self, event_name, **kwargs):
        event_dict = {
            'event_type': event_name,
            'event_time': self.timestamp,
            'event_source': 'ckan',
            'initiator_user_name': self.username,
            'org_id': self.org_id,
            'org_name': self.org_name,
            'dataset_name': self.dataset_name,
            'dataset_id': self.dataset_id,
        }
        for k, v in kwargs.items():
            event_dict[k] = v
        return event_dict

    def append_event(self, event: Event):
        self.change_events.append(event)

    def _detect_created_dataset(self):
        if not self.old_dataset_dict:
            changes = _find_dict_changes(self.old_dataset_dict, self.new_dataset_dict, DATASET_FIELDS)
            if changes:
                list_of_changes = list(changes.values())
                event_dict = self.create_event_dict(EVENT_TYPE_DATASET_CREATED, changed_fields=list_of_changes)
                self.append_event(DatasetEvent(**event_dict))

    def _detect_deleted_dataset(self):
        if self.old_dataset_dict and self.new_dataset_dict:
            changes = _find_dict_changes(self.old_dataset_dict, self.new_dataset_dict, DATASET_FIELDS)
            if changes:
                list_of_changes = list(changes.values())
                event_dict = self.create_event_dict(EVENT_TYPE_DATASET_DELETED, changed_fields=list_of_changes)
                self.append_event(DatasetEvent(**event_dict))

    def _detect_metadata_changed_dataset(self):
        if self.old_dataset_dict:
            changes = _find_dict_changes(self.old_dataset_dict, self.new_dataset_dict, DATASET_FIELDS)
            self._detect_groups_change(changes)
            self._detect_tags_change(changes)
            self._detect_customviz_change(changes)
            if changes:
                list_of_changes = list(changes.values())
                event_dict = self.create_event_dict(EVENT_TYPE_DATASET_METADATA_CHANGED, changed_fields=list_of_changes)
                self.append_event(DatasetEvent(**event_dict))

    def _detect_groups_change(self, changes):
        created_groups, deleted_groups, _, _ = \
            _compare_lists(self.old_dataset_dict.get('groups', []), self.new_dataset_dict.get('groups', []),
                           lambda idx, group: group['name'])
        if created_groups or deleted_groups:
            changes['groups'] = {
                'field': 'groups',
                'added_items': list(created_groups),
                'removed_items': list(deleted_groups),
            }

    def _detect_tags_change(self, changes):
        created_tags, deleted_tags, _, _ = \
            _compare_lists(
                (tag for tag in self.old_dataset_dict.get('tags', []) if tag.get('vocabulary_id') == _VOCABULARY_ID),
                (tag for tag in self.new_dataset_dict.get('tags', []) if tag.get('vocabulary_id') == _VOCABULARY_ID),
                lambda idx, tag: tag['name']
            )
        if created_tags or deleted_tags:
            changes['tags'] = {
                'field': 'tags',
                'added_items': list(created_tags),
                'removed_items': list(deleted_tags),
            }

    def _detect_customviz_change(self, changes):
        created_customvizs, deleted_customvizs, _, _ = \
            _compare_lists(
                self.old_dataset_dict.get('customviz', []),
                self.new_dataset_dict.get('customviz', []),
                lambda idx, customviz: customviz['url']
            )
        if created_customvizs or deleted_customvizs:
            changes['customviz'] = {
                'field': 'customviz',
                'added_items': list(created_customvizs),
                'removed_items': list(deleted_customvizs),
            }

    def _detect_deleted_resources(self):
        for resource_id in self.deleted_resource_ids:
            old_resource = self.old_resources_map[resource_id]
            resource_name = old_resource['name']

            changes = _find_dict_changes(old_resource, {}, RESOURCE_FIELDS)
            if changes:
                list_of_changes = list(changes.values())
                event_dict = self.create_event_dict(
                    EVENT_TYPE_RESOURCE_DELETED,
                    resource_name=resource_name,
                    resource_id=resource_id,
                    changed_fields=list_of_changes,
                )

                self.append_event(ResourceEvent(**event_dict))

    def _detect_created_resources(self):
        for resource_id in self.created_resource_ids:
            new_resource = self.new_resources_map[resource_id]
            resource_name = new_resource['name']

            changes = _find_dict_changes({}, new_resource, RESOURCE_FIELDS)
            if changes:
                list_of_changes = list(changes.values())
                event_dict = self.create_event_dict(
                    EVENT_TYPE_RESOURCE_CREATED,
                    resource_name=resource_name,
                    resource_id=resource_id,
                    changed_fields=list_of_changes,
                )
                self.append_event(ResourceEvent(**event_dict))

    def _detect_changed_resources(self):
        for resource_id in self.common_resource_ids:
            old_resource = self.old_resources_map[resource_id]
            new_resource = self.new_resources_map[resource_id]
            ResourceChangeDetector(self, old_resource, new_resource).detect_changes()

    def _replace_needed_values(self):
        if self.old_dataset_dict:
            self.old_dataset_dict['owner_org'] = self.old_dataset_dict.get('organization', {}).get('id') \
                if self.old_dataset_dict.get('organization') else None
        if self.new_dataset_dict:
            self.new_dataset_dict['owner_org'] = self.new_dataset_dict.get('organization', {}).get('id') \
                if self.new_dataset_dict.get('organization') else None


class ResourceChangeDetector(object):

    def __init__(self, dataset_detector: DatasetChangeDetector, old_resource: dict, new_resource: dict) -> None:
        super().__init__()
        self.dataset_detector = dataset_detector
        self.old_resource = old_resource
        self.new_resource = new_resource
        self.resource_id = new_resource['id']
        self.resource_name = new_resource['name']
        self.created_sheets = None
        self.deleted_sheets = None
        self.new_sheets_map = None
        self.old_sheets_map = None
        self.new_fs_item = None
        self.old_fs_item = None

    def create_event_dict(self, event_name, **kwargs) -> dict:
        event_dict = self.dataset_detector.create_event_dict(event_name, **kwargs)
        event_dict['resource_id'] = self.resource_id
        event_dict['resource_name'] = self.resource_name
        return event_dict

    def append_event(self, event: Event):
        self.dataset_detector.append_event(event)

    def detect_changes(self):
        self._detect_data_modified()
        self._detect_metadata_changed()
        self._detect_file_structure_change()

    def _detect_data_modified(self):
        key = 'last_modified'
        changes = _find_dict_changes(self.old_resource, self.new_resource, {key})
        if changes:
            list_of_changes = list(changes.values())
            event_dict = self.create_event_dict(EVENT_TYPE_RESOURCE_DATA_CHANGED, changed_fields=list_of_changes)
            self.append_event(ResourceEvent(**event_dict))

    def _detect_metadata_changed(self):
        changes = _find_dict_changes(self.old_resource, self.new_resource, RESOURCE_FIELDS)
        if changes:
            list_of_changes = list(changes.values())
            event_dict = self.create_event_dict(EVENT_TYPE_RESOURCE_METADATA_CHANGED, changed_fields=list_of_changes)
            self.append_event(ResourceEvent(**event_dict))

    def _detect_file_structure_change(self):
        new_fs_history_str: str = self.new_resource.get('fs_check_info')
        old_fs_history_str: str = self.old_resource.get('fs_check_info')
        if new_fs_history_str and new_fs_history_str != old_fs_history_str:
            try:
                fs_history = json.loads(new_fs_history_str)
                history_items = [item for item in fs_history if item.get('state') == 'success']
                if len(history_items) >= 2:
                    self.new_fs_item = history_items[-1]
                    self.old_fs_item = history_items[-2]

                    self.detect_fs_item_changes()
            except Exception as e:
                log.error(str(e))

    def detect_fs_item_changes(self):
        last_item_sheets = None
        prev_item_sheets = None
        if self.new_fs_item:
            last_item_sheets = self.new_fs_item.get('hxl_proxy_response', {}).get('sheets') or []
        if self.old_fs_item:
            prev_item_sheets = self.old_fs_item.get('hxl_proxy_response', {}).get('sheets') or []
        if last_item_sheets and prev_item_sheets:
            self.created_sheets, self.deleted_sheets, self.new_sheets_map, self.old_sheets_map = \
                _compare_lists(prev_item_sheets, last_item_sheets,
                               lambda i, sheet: sheet.get('name') or str(i))

            self._detect_created_sheets()
            self._detect_deleted_sheets()
            self._detect_changed_sheets()

    def _detect_created_sheets(self):
        for sheet_id in self.created_sheets:
            event_dict = self.create_event_dict(EVENT_TYPE_SPREADSHEET_SHEET_CREATED,
                                                sheet_id=sheet_id, changed_fields=None)
            self.append_event(FileStructureEvent(**event_dict))

    def _detect_deleted_sheets(self):
        for sheet_id in self.deleted_sheets:
            event_dict = self.create_event_dict(EVENT_TYPE_SPREADSHEET_SHEET_DELETED,
                                                sheet_id=sheet_id, changed_fields=None)
            self.append_event(FileStructureEvent(**event_dict))

    def _detect_changed_sheets(self):
        common_sheet_ids = set(self.old_sheets_map.keys()).intersection(self.new_sheets_map.keys())
        for sheet_id in common_sheet_ids:
            old_sheet = self.old_sheets_map[sheet_id]
            new_sheet = self.new_sheets_map[sheet_id]
            SpreadsheetChangeDetector(self, sheet_id, old_sheet, new_sheet).detect_changes()


class SpreadsheetChangeDetector(object):

    def __init__(self, resource_detector: ResourceChangeDetector, sheet_id: str, old_sheet: dict,
                 new_sheet: dict) -> None:
        super().__init__()
        self.sheet_id = sheet_id
        self.old_sheet = old_sheet
        self.new_sheet = new_sheet
        self.resource_detector = resource_detector

    def create_event_dict(self, **kwargs) -> dict:
        event_dict = self.resource_detector.create_event_dict(EVENT_TYPE_SPREADSHEET_SHEET_CHANGED, **kwargs)
        event_dict['sheet_id'] = self.sheet_id
        return event_dict

    def append_event(self, event: Event):
        self.resource_detector.append_event(event)

    def detect_changes(self):
        self._detect_internal_sheet_changes()

    def _detect_internal_sheet_changes(self):
        changes = _find_dict_changes(self.old_sheet, self.new_sheet, SPREADSHEET_FIELDS)
        if changes:
            list_of_changes = list(changes.values())
            event_dict = self.create_event_dict(changed_fields=list_of_changes)
            self.append_event(FileStructureEvent(**event_dict))


def _compare_lists(old_list: [dict], new_list: [dict], item_id_extractor: Callable[[int, dict], str]) -> \
        Tuple[Set[str], Set[str], Dict[str, Dict], Dict[str, Dict]]:
    '''
    Compares two lists of dictionaries and returns the IDs of created and deleted items,
    and dictionaries of old and new items.

    :param old_list: List of old dictionaries to compare.
    :param new_list: List of new dictionaries to compare.
    :param item_id_extractor: A callable that takes a dictionary item and returns a unique ID string for that item.
    :returns: A tuple of four elements containing the following:

             * `created_item_ids`: A set of IDs of new items.
             * `deleted_item_ids`: A set of IDs of old items that are not in the new list.
             * `new_items_map`: A dictionary mapping item IDs to items in the new list.
             * `old_items_map`: A dictionary mapping item IDs to items in the old list.
    '''
    old_items_map = {item_id_extractor(index, item): item for index, item in enumerate(old_list)}
    new_items_map = {item_id_extractor(index, item): item for index, item in enumerate(new_list)}
    deleted_item_ids = old_items_map.keys() - new_items_map.keys()
    created_item_ids = new_items_map.keys() - old_items_map.keys()
    return created_item_ids, deleted_item_ids, new_items_map, old_items_map


def _find_dict_changes(old_dict: dict, new_dict: dict, fields: Set[str] = None) -> Dict[str, dict]:
    if not fields:
        fields = set().union(old_dict.keys()).union(new_dict.keys())
    changes: Dict[str:dict] = {}
    for field in fields:
        old_value = old_dict.get(field)
        new_value = new_dict.get(field)
        if old_value != new_value:
            changes[field] = {
                'field': field,
                'new_value': new_value,
                'new_display_value': _get_display_value(field, new_dict, new_value),
                'old_value': old_value,
                'old_display_value': _get_display_value(field, old_dict, old_value),
            }
    return changes


def _get_display_value(field, source_dict, default_value=None):
    if field == 'owner_org':
        return source_dict.get('organization', {}).get('title') \
            if source_dict.get('organization') else None
    elif field == 'subnational':
        return 'subnational' if default_value == '1' else 'not subnational'
    elif field == 'dataset_date':
        return get_date_from_concat_str(default_value)
    elif field == 'data_update_frequency':
        return get_frequency_by_value(default_value)
    elif field == 'license_id':
        return get_license_name_by_value(default_value)
    elif field == 'microdata':
        return 'contains microdata' if default_value else 'does not contain microdata'
    return default_value


def _filter_dict_certain_keys(source_dict: dict, parent_key: str, keys_to_keep: dict):
    for key, value in list(source_dict.items()):
        if key not in keys_to_keep[parent_key]:
            source_dict.pop(key)
        elif isinstance(value, dict):
            source_dict[key] = _filter_dict_certain_keys(value, key, keys_to_keep)
        elif isinstance(value, list):
            source_dict[key] = [_filter_dict_certain_keys(el, key, keys_to_keep) if isinstance(el, dict) else el for el
                                in value]
    return source_dict

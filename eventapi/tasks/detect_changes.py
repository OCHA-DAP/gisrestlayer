import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

from typing import Set, Dict, Callable, Tuple

from eventapi.helpers.stream_redis import stream_events_to_redis

log = logging.getLogger(__name__)

EVENT_TYPE_DATASET_CREATED = 'dataset-created'
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


@dataclass
class Event(object):
    event_type: str
    event_time: str
    event_source: str
    # initiator_user_id: str
    initiator_user_name: str


@dataclass
class DatasetEvent(Event):
    dataset_name: str
    dataset_id: str
    changed_fields: [dict]


@dataclass
class ResourceEvent(Event):
    dataset_name: str
    dataset_id: str
    changed_fields: [dict]
    resource_name: str
    resource_id: str


@dataclass
class FileStructureEvent(ResourceEvent):
    sheet_id: str


def detect_changes(task_arguments):
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

    FIELDS = {
        'name', 'title', 'notes', 'subnational', 'dataset_source', 'owner_org', 'dataset_date',
        'data_update_frequency', 'data_update_frequency', 'license_id', 'license_other',
        'methodology', 'methodology_other', 'caveats', 'archived', 'is_requestdata_type',
    }

    def __init__(self, username: str, old_dataset_dict: dict, new_dataset_dict: dict) -> None:
        super().__init__()
        self.change_events: [Event] = []
        self.timestamp = datetime.utcnow().isoformat()
        self.username = username
        self.old_dataset_dict = old_dataset_dict
        self.new_dataset_dict = new_dataset_dict

        self.dataset_id = new_dataset_dict['id']
        self.dataset_name = new_dataset_dict['name']

        self.created_resource_ids, self.deleted_resource_ids, self.new_resources_map, self.old_resources_map = \
            _compare_lists(old_dataset_dict.get('resources', []), new_dataset_dict.get('resources', []),
                           lambda idx, resource_dict: resource_dict['id'])

        self.old_resources_map = {r['id']:r for r in old_dataset_dict.get('resources', [])}
        self.new_resources_map = {r['id']:r for r in new_dataset_dict.get('resources', [])}

        self.common_resource_ids = set(self.old_resources_map.keys()).intersection(self.new_resources_map.keys())

    def detect_changes(self):
        self._detect_created_dataset()
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
            'dataset_name': self.dataset_name,
            'dataset_id': self.dataset_id,
        }
        for k,v in kwargs.items():
            event_dict[k] = v
        return event_dict

    def append_event(self, event: Event):
        self.change_events.append(event)

    def _detect_created_dataset(self):
        if not self.old_dataset_dict:
            event_dict = self.create_event_dict(EVENT_TYPE_DATASET_CREATED, changed_fields=None)
            self.append_event(DatasetEvent(**event_dict))

    def _detect_metadata_changed_dataset(self):
        if self.old_dataset_dict:
            changes = _find_dict_changes(self.old_dataset_dict, self.new_dataset_dict, self.FIELDS)
            self._detect_groups_change(changes)
            self._detect_tags_change(changes)
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

    def _detect_deleted_resources(self):
        for resource_id in self.deleted_resource_ids:
            resource_name = self.old_resources_map[resource_id]['name']
            event_dict = self.create_event_dict(
                EVENT_TYPE_RESOURCE_DELETED,
                resource_name=resource_name,
                resource_id=resource_id,
                changed_fields=None,
            )

            self.append_event(ResourceEvent(**event_dict))

    def _detect_created_resources(self):
        for resource_id in self.created_resource_ids:
            resource_name = self.new_resources_map[resource_id]['name']
            event_dict = self.create_event_dict(
                EVENT_TYPE_RESOURCE_CREATED,
                resource_name=resource_name,
                resource_id=resource_id,
                changed_fields=None,
            )
            self.append_event(ResourceEvent(**event_dict))

    def _detect_changed_resources(self):
        for resource_id in self.common_resource_ids:
            old_resource = self.old_resources_map[resource_id]
            new_resource = self.new_resources_map[resource_id]
            ResourceChangeDetector(self, old_resource, new_resource).detect_changes()


class ResourceChangeDetector(object):

    FIELDS = {'name', 'format', 'description', 'microdata', 'resource_type', 'url'}

    def __init__(self, dataset_detector:DatasetChangeDetector, old_resource: dict, new_resource:dict) -> None:
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
        if self.old_resource[key] != self.new_resource[key]:
            event_dict = self.create_event_dict(EVENT_TYPE_RESOURCE_DATA_CHANGED, changed_fields=None)
            self.append_event(ResourceEvent(**event_dict))

    def _detect_metadata_changed(self):
        changes = _find_dict_changes(self.old_resource, self.new_resource, self.FIELDS)
        if changes:
            list_of_changes = list(changes.values())
            event_dict = self.create_event_dict(EVENT_TYPE_RESOURCE_METADATA_CHANGED, changed_fields=list_of_changes)
            self.append_event(ResourceEvent(**event_dict))

    def _detect_file_structure_change(self):
        last_item_sheets = None
        prev_item_sheets = None
        new_fs_history_str: str = self.new_resource.get('fs_check_info')
        old_fs_history_str: str = self.old_resource.get('fs_check_info')
        if new_fs_history_str and new_fs_history_str != old_fs_history_str:
            try:
                fs_history = json.loads(new_fs_history_str)
                history_items = [item for item in fs_history if item.get('state') == 'success']
                if len(history_items) >= 2:
                    last_item = history_items[-1]
                    prev_item = history_items[-2]
                    if last_item:
                        last_item_sheets = last_item.get('hxl_proxy_response', {}).get('sheets') or []
                    if prev_item:
                        prev_item_sheets = prev_item.get('hxl_proxy_response', {}).get('sheets') or []
            except Exception as e:
                log.error(str(e))

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
    FIELDS = {'nrows', 'ncols', 'header_hash', 'hashtag_hash', 'hxl_header_hash', 'name'}

    def __init__(self, resource_detector: ResourceChangeDetector, sheet_id:str, old_sheet: dict, new_sheet:dict) -> None:
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
        changes = _find_dict_changes(self.old_sheet, self.new_sheet, self.FIELDS)
        if changes:
            list_of_changes = list(changes.values())
            event_dict = self.create_event_dict(changed_fields=list_of_changes)
            self.append_event(FileStructureEvent(**event_dict))


def _compare_lists(old_list: [dict], new_list: [dict], item_id_extractor: Callable[[int, dict], str]) -> \
        Tuple[ Set[str], Set[str], Dict[str, Dict], Dict[str, Dict]]:
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
                'old_value': old_value,
            }
    return changes

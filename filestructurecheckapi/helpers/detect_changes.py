from typing import List

from eventapi.tasks.detect_changes import ResourceChangeDetector, Event, FileStructureEvent


def detect_file_structure_changes(new_fs_item: dict, old_fs_item: dict) -> List[FileStructureEvent]:
    detector = FileStructureChangeDetector(new_fs_item, old_fs_item)
    detector.detect_fs_item_changes()
    return  detector.change_events


class FileStructureChangeDetector(ResourceChangeDetector):

    def __init__(self, new_fs_item: dict, old_fs_item: dict) -> None:
        super().__init__(None, None, {'id': None, 'name': None})
        self.change_events: [FileStructureEvent] = []
        self.new_fs_item = new_fs_item
        self.old_fs_item = old_fs_item

    def create_event_dict(self, event_name, **kwargs) -> dict:
        event_dict = {
            'event_type': event_name,
            'event_time': None,
            'event_source': None,
            'initiator_user_name': None,
            'dataset_name': None,
            'dataset_id': None,
            'dataset_obj': None,
            'resource_name': None,
            'resource_id': None,
        }
        for k, v in kwargs.items():
            event_dict[k] = v
        return event_dict

    def append_event(self, event: Event):
        self.change_events.append(event)
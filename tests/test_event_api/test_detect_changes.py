from typing import cast, Optional

from eventapi.tasks.detect_changes import detect_changes, EVENT_TYPE_DATASET_METADATA_CHANGED, DatasetEvent, \
    ResourceEvent, EVENT_TYPE_RESOURCE_DELETED, EVENT_TYPE_RESOURCE_CREATED, EVENT_TYPE_RESOURCE_DATA_CHANGED, \
    EVENT_TYPE_RESOURCE_METADATA_CHANGED, EVENT_TYPE_DATASET_CREATED
from tests.test_event_api.sample_data import OLD_DATASET_DICT, NEW_DATASET_DICT


def test_detect_changes_new_dataset():
    events = detect_changes({
        'username': 'test_username',
        'old_dataset_dict': {},
        'new_dataset_dict': NEW_DATASET_DICT,
    })
    assert len(events) == 3, '1 dataset-created, 2 resource-created'

    dataset_created_event: Optional[DatasetEvent] = \
        next((e for e in events if e.event_type == EVENT_TYPE_DATASET_CREATED), None)
    assert dataset_created_event, 'A dataset-created event needs to exist'
    assert len(dataset_created_event.changed_fields) > 1

    resource_created_event: Optional[ResourceEvent] = \
        next((e for e in events if e.event_type == EVENT_TYPE_RESOURCE_CREATED), None)
    assert resource_created_event, 'A resource-created event needs to exist'
    assert len(resource_created_event.changed_fields) > 1


def test_detect_changes_updated_dataset():
    events = detect_changes({
        'username': 'test_username',
        'old_dataset_dict': OLD_DATASET_DICT,
        'new_dataset_dict': NEW_DATASET_DICT,
    })
    assert len(events) == 6, '1 dataset-metadata-changed, 1 resource-deleted, 1 resource-created,' \
                             '1 resource-metadata-changed, 1 resource-data'

    dataset_metadata_changed = cast(DatasetEvent,
                                    next((e for e in events if e.event_type == EVENT_TYPE_DATASET_METADATA_CHANGED),
                                         None))

    assert dataset_metadata_changed.dataset_name == 'search-test-dataset-1'
    assert {'data_update_frequency', 'notes', 'groups', 'tags'} == \
           {item['field'] for item in dataset_metadata_changed.changed_fields}

    resource_deleted = cast(ResourceEvent,
                                    next((e for e in events if e.event_type == EVENT_TYPE_RESOURCE_DELETED), None))
    assert resource_deleted.resource_name == 'belgium.geojson'

    resource_created = cast(ResourceEvent,
                            next((e for e in events if e.event_type == EVENT_TYPE_RESOURCE_CREATED), None))
    assert resource_created.resource_name == 'belgium2.geojson'

    resource_data_changed = cast(ResourceEvent,
                            next((e for e in events if e.event_type == EVENT_TYPE_RESOURCE_DATA_CHANGED), None))
    assert resource_data_changed.resource_name == 'test2.csv'

    resource_metadata_changed = cast(ResourceEvent,
                                 next((e for e in events if e.event_type == EVENT_TYPE_RESOURCE_METADATA_CHANGED), None))
    assert resource_metadata_changed.resource_name == 'test2.csv'
    assert {'name', 'description'} == \
           {item['field'] for item in resource_metadata_changed.changed_fields}

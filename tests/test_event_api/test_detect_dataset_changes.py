from tests.test_event_api.sample_data import NEW_DATASET_DICT, OLD_DATASET_DICT
from eventapi.tasks.detect_changes import DatasetChangeDetector, EVENT_TYPE_DATASET_METADATA_CHANGED


def test_dataset_changed_data_during_init():
    new_dataset_dict = NEW_DATASET_DICT
    old_dataset_dict = OLD_DATASET_DICT

    detector = DatasetChangeDetector(new_dataset_dict=new_dataset_dict.copy(), old_dataset_dict=old_dataset_dict.copy(),
                                     username='test_user')

    assert detector.new_dataset_dict == new_dataset_dict, 'new dataset dict should be the same'
    assert detector.old_dataset_dict == old_dataset_dict, 'old dataset dict should be the same'


def test_detect_dataset_changes():
    change_events = _detect_dataset_changes(NEW_DATASET_DICT, OLD_DATASET_DICT)

    dataset_metadata_changed_events = [e for e in change_events if e.event_type == EVENT_TYPE_DATASET_METADATA_CHANGED]
    assert len(dataset_metadata_changed_events) == 1, 'one dataset should have been modified'

    modified_event = dataset_metadata_changed_events[0]

    assert modified_event.dataset_obj.get('id') == OLD_DATASET_DICT.get('id')

    assert len(modified_event.changed_fields) == 4
    assert {'data_update_frequency', 'notes', 'groups', 'tags'} == {item['field'] for item in
                                                                    modified_event.changed_fields}


def _detect_dataset_changes(new_dataset_item: dict, old_dataset_item: dict):
    detector = DatasetChangeDetector(new_dataset_dict=new_dataset_item, old_dataset_dict=old_dataset_item,
                                     username='test_user')
    detector.detect_changes()
    return detector.change_events

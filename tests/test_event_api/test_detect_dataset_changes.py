from tests.test_event_api.sample_data import NEW_DATASET_DICT, OLD_DATASET_DICT
from eventapi.tasks.detect_changes import DatasetChangeDetector, EVENT_TYPE_DATASET_METADATA_CHANGED
from eventapi.helpers.helpers import get_frequency_by_value, get_license_name_by_value


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


def test_display_values_dataset_changes():
    dataset_dict = NEW_DATASET_DICT.copy()
    updated_dataset_dict = NEW_DATASET_DICT.copy()

    new_frequency = '365'
    new_license = 'hdx-multi'
    new_org = {
        'id': '1b23xc5a-32aa-123a-456b-890abc12fgh9',
        'name': 'hdx',
        'title': 'HDX',
        'type': 'organization',
        'description': 'A second test organization for demonstrations.',
        'image_url': '',
        'created': '2019-01-10T01:30:02.101702',
        'is_organization': True,
        'approval_status': 'approved',
        'state': 'active'
    }

    updated_dataset_dict['organization'] = new_org
    updated_dataset_dict['owner_org'] = new_org.get('id')
    updated_dataset_dict['data_update_frequency'] = new_frequency
    updated_dataset_dict['license_id'] = new_license
    updated_dataset_dict['subnational'] = 0
    updated_dataset_dict['dataset_date'] = '[2022-03-03T00:00:00 TO 2022-03-10T00:00:00]'

    change_events = _detect_dataset_changes(updated_dataset_dict, dataset_dict)
    changed_fields = change_events[0].changed_fields

    updated_fields = {'owner_org', 'data_update_frequency', 'subnational', 'dataset_date', 'license_id'}

    assert len(changed_fields) == len(updated_fields)
    assert updated_fields == {item['field'] for item in changed_fields}

    for changed_field in changed_fields:
        display_value = changed_field['new_display_value']
        if changed_field['field'] == 'owner_org':
            assert new_org.get('title') in display_value
        elif changed_field['field'] == 'data_update_frequency':
            assert get_frequency_by_value(new_frequency) in display_value
        elif changed_field['field'] == 'subnational':
            assert 'not subnational' in display_value
        elif changed_field['field'] == 'dataset_date':
            assert 'March' in display_value
        elif changed_field['field'] == 'license_id':
            assert get_license_name_by_value(new_license) in display_value


def _detect_dataset_changes(new_dataset_item: dict, old_dataset_item: dict):
    detector = DatasetChangeDetector(new_dataset_dict=new_dataset_item, old_dataset_dict=old_dataset_item,
                                     username='test_user')
    detector.detect_changes()
    return detector.change_events

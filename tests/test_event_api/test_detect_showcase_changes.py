from eventapi.tasks.detect_changes import DatasetChangeDetector

NEW_SHOWCASE_DICT = {
    "creator_user_id": "7c92b9f6-f898-4302-9f73-61ec8eab1340",
    "id": "bbbf9782-a3d0-4885-8c16-d34cc05febbb",
    "metadata_created": "2023-07-03T04:25:20.082653",
    "metadata_modified": "2023-07-03T04:25:20.082659",
    "name": "test-showcase-for-change-detection",
    "notes": "Test showcase - description",
    "num_tags": 2,
    "state": "active",
    "title": "Test showcase for change detection",
    "type": "showcase",
    "tags": [
        {
            "display_name": "hxl",
            "id": "a0fbb23a-6aad-4ccc-8062-e9ef9f20e5d2",
            "name": "hxl",
            "state": "active",
            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1"
        },
        {
            "display_name": "indicators",
            "id": "08dade96-0bf4-4248-9d9f-421f7b844e53",
            "name": "indicators",
            "state": "active",
            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1"
        }
    ],
}


def test_dataset_changed_data_during_init():
    new_showcase_dict = NEW_SHOWCASE_DICT

    detector = DatasetChangeDetector('test-user', {}, new_showcase_dict)

    detector.detect_changes()
    assert len(detector.change_events) == 0, 'No events should be generated for showcases'

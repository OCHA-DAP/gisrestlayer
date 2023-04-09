from eventapi.tasks.detect_changes import EVENT_TYPE_SPREADSHEET_SHEET_CREATED, EVENT_TYPE_SPREADSHEET_SHEET_CHANGED
from filestructurecheckapi.helpers.detect_changes import detect_file_structure_changes

new_item = {
    "state": "success",
    "message": "Hxl Proxy data received successfully",
    "timestamp": "2023-04-07T04:00:48.495831",
    "hxl_proxy_response": {
        "url_or_filename": "https://test.domain.test/download/some_test.xlsx",
        "format": "XLSX",
        "sheets": [
            {
                "name": "Sheet1",
                "is_hidden": False,
                "nrows": 17,
                "ncols": 27,
                "has_merged_cells": True,
                "is_hxlated": False,
                "header_hash": "af80aeac4770a319cb666f752149143e",
                "hashtag_hash": None
            },
            {
                "name": "Sheet2",
                "is_hidden": False,
                "nrows": 17,
                "ncols": 27,
                "has_merged_cells": True,
                "is_hxlated": False,
                "header_hash": "af80aeac4770a319cb666f752149143e",
                "hashtag_hash": None
            }
        ]
    }
}

old_item = {
    "state": "success",
    "message": "Hxl Proxy data received successfully",
    "timestamp": "2023-04-07T04:00:48.495831",
    "hxl_proxy_response": {
        "url_or_filename": "https://test.domain.test/download/some_test.xlsx",
        "format": "XLSX",
        "sheets": [
            {
                "name": "Sheet1",
                "is_hidden": False,
                "nrows": 10,
                "ncols": 22,
                "has_merged_cells": True,
                "is_hxlated": False,
                "header_hash": "af80aeac4770a319cb666f752149143e",
                "hashtag_hash": None
            }
        ]
    }
}


def test_detect_changes():
    change_events = detect_file_structure_changes(new_item, old_item)
    sheet_created_events = [e for e in change_events if e.event_type == EVENT_TYPE_SPREADSHEET_SHEET_CREATED]
    assert len(sheet_created_events) == 1, 'one new sheet should have been created'

    sheet_modified_events = [e for e in change_events if e.event_type == EVENT_TYPE_SPREADSHEET_SHEET_CHANGED]
    assert len(sheet_modified_events) == 1, 'one sheet should have been modified'
    modified_event = sheet_modified_events[0]
    assert modified_event.sheet_id == 'Sheet1'
    assert len(modified_event.changed_fields) == 2
    assert {'ncols', 'nrows'} == {item['field'] for item in modified_event.changed_fields}

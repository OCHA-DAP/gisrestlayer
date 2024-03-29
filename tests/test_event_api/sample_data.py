# The sample data contains 2 dataset dictionaries (new and old). The differences are in the following fields:
# - data_update_frequency
# - notes
# - groups (1 extra group was added)
# - tags (1 tag was removed)
# - resources
#   - 1 resource was deleted
#   - 1 resource was created
#   - 1 resource data was modified (the last_modified field) and 1 metadata field was modified: description


NEW_DATASET_DICT = {
    "archived": False,
    "caveats": 'comment',
    "creator_user_id": "7c92b9f6-f898-4302-9f73-61ec8eab1340",
    "data_update_frequency": "60",
    "dataset_date": "[2022-03-03T00:00:00 TO *]",
    "dataset_preview": "first_resource",
    "dataset_source": "none",
    "due_date": "2023-05-03T11:03:01",
    "has_geodata": True,
    "has_quickcharts": False,
    "has_showcases": False,
    "id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
    "is_requestdata_type": False,
    "isopen": True,
    "last_modified": "2023-04-03T11:03:01.810847",
    "license_id": "cc-by",
    "license_title": "Creative Commons Attribution International",
    "license_url": "http://www.opendefinition.org/licenses/cc-by",
    "maintainer": "7c92b9f6-f898-4302-9f73-61ec8eab1340",
    "maintainer_email": None,
    "metadata_created": "2020-08-11T22:31:01.059136",
    "metadata_modified": "2023-04-09T22:29:13.291241",
    "methodology": "Census",
    "name": "search-test-dataset-1",
    "notes": "This is a test dataset. (MODIFIED)",
    "num_resources": 3,
    "num_tags": 1,
    "organization": {
        "id": "5a63012e-6c41-420c-8c33-e84b277fdc90",
        "name": "innago",
        "title": "INNAGO",
        "type": "organization",
        "description": "A test organization for demonstrations .",
        "image_url": "",
        "created": "2014-07-14T08:29:25.133079",
        "is_organization": True,
        "approval_status": "approved",
        "state": "active"
    },
    "overdue_date": "2023-05-17T11:03:01",
    "owner_org": "5a63012e-6c41-420c-8c33-e84b277fdc90",
    "package_creator": "alexg",
    "pageviews_last_14_days": 17,
    "private": False,
    "qa_completed": False,
    "state": "active",
    "subnational": "1",
    "title": "Search test dataset 1",
    "total_res_downloads": 5,
    "type": "dataset",
    "url": None,
    "version": None,
    "groups": [
        {
            "description": "No description",
            "display_name": "Romania",
            "id": "c92bd69f-54c0-4d02-ad30-d33fd1cd1393",
            "image_display_url": "",
            "name": "rou",
            "title": "Romania"
        },
        {
            "description": "No description",
            "display_name": "Belgium",
            "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "image_display_url": "",
            "name": "bel",
            "title": "Belgium"
        }
    ],
    "resources": [
        {
            "alt_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/",
            "cache_last_updated": None,
            "cache_url": None,
            "created": "2023-03-24T16:09:24.205520",
            "datastore_active": False,
            "description": "Modified description",
            "download_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "format": "CSV",
            "hash": "",
            "hdx_rel_url": "/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "id": "befd658a-c85e-40d0-991c-69feb2add47b",
            "last_modified": "2023-03-25T16:09:23.986662",
            "metadata_modified": "2023-04-09T22:29:13.296578",
            "microdata": False,
            "mimetype": "text/csv",
            "mimetype_inner": None,
            "name": "test2.csv",
            "originalHash": -339678183,
            "package_id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
            "pii": "False",
            "position": 1,
            "resource_type": "file.upload",
            "size": 24,
            "state": "active",
            "url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "url_type": "upload"
        },
        {
            "alt_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/",
            "cache_last_updated": None,
            "cache_url": None,
            "created": "2022-05-05T10:29:44.662447",
            "datastore_active": False,
            "description": "33354",
            "download_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "format": "GeoJSON",
            "hash": "",
            "hdx_rel_url": "/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "id": "a3d389da-7b9b-402c-aaf4-6c2e05a78cda",
            "last_modified": "2023-02-07T15:56:39.687000",
            "metadata_modified": "2023-03-24T16:24:37.795195",
            "microdata": False,
            "mimetype": "application/geo+json",
            "mimetype_inner": None,
            "name": "belgium2.geojson",
            "originalHash": 374994550,
            "package_id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
            "pii": "False",
            "position": 2,
            "resource_type": "file.upload",
            "shape_info": "[{\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-22T23:51:57.501970\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-22T23:52:03.459353\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T15:54:49.558545\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T15:54:50.255149\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:00:55.225856\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:00:56.096149\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:09:25.507691\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:09:29.694416\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:24:36.917339\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:24:37.685465\"}]",
            "size": 2198,
            "state": "active",
            "url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "url_type": "upload"
        }
    ],
    "tags": [
        {
            "display_name": "nutrition",
            "id": "5cd44eef-f868-47d8-afb4-7d7d63154533",
            "name": "nutrition",
            "state": "active",
            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1"
        },
    ],
    "relationships_as_subject": [],
    "relationships_as_object": [],
    "is_fresh": True,
    "update_status": "fresh",
}

OLD_DATASET_DICT = {
    "archived": False,
    "caveats": 'comment',
    "creator_user_id": "7c92b9f6-f898-4302-9f73-61ec8eab1340",
    "data_update_frequency": "30",
    "dataset_date": "[2022-03-03T00:00:00 TO *]",
    "dataset_preview": "first_resource",
    "dataset_source": "none",
    "due_date": "2023-05-03T11:03:01",
    "has_geodata": True,
    "has_quickcharts": False,
    "has_showcases": False,
    "id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
    "is_requestdata_type": False,
    "isopen": True,
    "last_modified": "2023-04-03T11:03:01.810847",
    "license_id": "cc-by",
    "license_title": "Creative Commons Attribution International",
    "license_url": "http://www.opendefinition.org/licenses/cc-by",
    "maintainer": "7c92b9f6-f898-4302-9f73-61ec8eab1340",
    "maintainer_email": None,
    "metadata_created": "2020-08-11T22:31:01.059136",
    "metadata_modified": "2023-04-09T22:29:13.291241",
    "methodology": "Census",
    "name": "search-test-dataset-1",
    "notes": "This is a test dataset",
    "num_resources": 3,
    "num_tags": 1,
    "organization": {
        "id": "5a63012e-6c41-420c-8c33-e84b277fdc90",
        "name": "innago",
        "title": "INNAGO",
        "type": "organization",
        "description": "A test organization for demonstrations .",
        "image_url": "",
        "created": "2014-07-14T08:29:25.133079",
        "is_organization": True,
        "approval_status": "approved",
        "state": "active"
    },
    "overdue_date": "2023-05-17T11:03:01",
    "owner_org": "5a63012e-6c41-420c-8c33-e84b277fdc90",
    "package_creator": "alexg",
    "pageviews_last_14_days": 17,
    "private": False,
    "qa_completed": False,
    "state": "active",
    "subnational": "1",
    "title": "Search test dataset 1",
    "total_res_downloads": 5,
    "type": "dataset",
    "url": None,
    "version": None,
    "groups": [
        {
            "description": "No description",
            "display_name": "Romania",
            "id": "c92bd69f-54c0-4d02-ad30-d33fd1cd1393",
            "image_display_url": "",
            "name": "rou",
            "title": "Romania"
        }
    ],
    "resources": [
        {
            "alt_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/",
            "cache_last_updated": None,
            "cache_url": None,
            "created": "2023-03-24T16:09:24.205520",
            "datastore_active": False,
            "description": "Description",
            "download_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "format": "CSV",
            "hash": "",
            "hdx_rel_url": "/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "id": "befd658a-c85e-40d0-991c-69feb2add47b",
            "last_modified": "2023-03-24T16:09:23.986662",
            "metadata_modified": "2023-04-09T22:29:13.296578",
            "microdata": False,
            "mimetype": "text/csv",
            "mimetype_inner": None,
            "name": "test1.csv",
            "originalHash": -339678183,
            "package_id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
            "pii": "False",
            "position": 1,
            "resource_type": "file.upload",
            "size": 24,
            "state": "active",
            "url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/befd658a-c85e-40d0-991c-69feb2add47b/download/test1.csv",
            "url_type": "upload"
        },
        {
            "alt_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/",
            "cache_last_updated": None,
            "cache_url": None,
            "created": "2022-05-05T10:29:44.662447",
            "datastore_active": False,
            "description": "33354",
            "download_url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "format": "GeoJSON",
            "hash": "",
            "hdx_rel_url": "/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "id": "f3d389da-7b9b-402c-aaf4-6c2e05a78cd4",
            "last_modified": "2023-02-07T15:56:39.687000",
            "metadata_modified": "2023-03-24T16:24:37.795195",
            "microdata": False,
            "mimetype": "application/geo+json",
            "mimetype_inner": None,
            "name": "belgium.geojson",
            "originalHash": 374994550,
            "package_id": "1a4dfde8-ce43-45ce-9a78-6727af9f132f",
            "pii": "False",
            "position": 2,
            "resource_type": "file.upload",
            "shape_info": "[{\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-22T23:51:57.501970\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-22T23:52:03.459353\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T15:54:49.558545\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T15:54:50.255149\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:00:55.225856\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:00:56.096149\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:09:25.507691\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:09:29.694416\"}, {\"state\": \"processing\", \"message\": \"The processing of the geo-preview has started\", \"layer_id\": \"None\", \"error_type\": \"None\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:24:36.917339\"}, {\"state\": \"failure\", \"message\": \"Error in communication with geopreview stack\", \"layer_id\": \"None\", \"error_type\": \"ckan-generated-error\", \"error_class\": \"None\", \"timestamp\": \"2023-03-24T16:24:37.685465\"}]",
            "size": 2198,
            "state": "active",
            "url": "https://data.humdata.local/dataset/1a4dfde8-ce43-45ce-9a78-6727af9f132f/resource/f3d389da-7b9b-402c-aaf4-6c2e05a78cd4/download/belgium.geojson",
            "url_type": "upload"
        }
    ],
    "tags": [
        {
            "display_name": "nutrition",
            "id": "5cd44eef-f868-47d8-afb4-7d7d63154533",
            "name": "nutrition",
            "state": "active",
            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1"
        },
        {
            "display_name": "geodata",
            "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "name": "geodata",
            "state": "active",
            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1"
        }
    ],
    "relationships_as_subject": [],
    "relationships_as_object": [],
    "is_fresh": True,
    "update_status": "fresh",
}


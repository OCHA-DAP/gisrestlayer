import os
from unittest import mock

import pytest

from importapi.tasks.create_preview import CreatePreviewTask

API_KEY = 'TEST_API_KEY'
CKAN_DOWNLOAD_URL = 'http://ckantest/dataset/some_dataset_id/resource/some_resource_id/download'


class FakeResponse(object):
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        yield b'{}'

    def close(self):
        pass


@pytest.fixture()
def task_args(tmp_path, monkeypatch):
    monkeypatch.setenv('HDX_GIS_API_KEY', API_KEY)
    return {
        'verify_ckan_ssl': True,
        'ckan_base_url': 'http://ckantest',
        'download_chunk_size': 1024,
        'max_file_size_mb': 1024 * 1024,
        'timeout_sec': 10,
        'table_name_prefix': 'testpre',
        'ckan_api_base_url': 'http://ckantest/api/action',
        'resource_update_action': 'hdx_resource_update_metadata',
        'gis_api_pattern': 'http://gisapi/services/tables/{table_name}',
        'hdx_user_agent': 'TEST_USER_AGENT',
        'tmp_download_directory': str(tmp_path / 'downloads'),

        'dataset_id': 'some_dataset_id',
        'resource_id': 'some_resource_id',
        'download_url': 'https://ckantest/dataset/some_dataset_id/resource/some_resource_id/download/test.geojson',
        'url_type': 'upload',
    }


def _download(task_args, response):
    task = CreatePreviewTask(task_args)
    with mock.patch('importapi.tasks.create_preview.requests.get', return_value=response) as mocked_get:
        filepath = task.download_file('testpre_layer')
    return filepath, mocked_get


def test_uploaded_file_is_downloaded_from_configured_ckan(task_args):
    # even a malicious download url is ignored for uploads: the key only goes to the configured CKAN
    task_args['download_url'] = 'http://attacker.example/test.geojson?x=ckantest'
    filepath, mocked_get = _download(task_args, FakeResponse(CKAN_DOWNLOAD_URL))

    assert mocked_get.call_args[0][0] == CKAN_DOWNLOAD_URL
    assert mocked_get.call_args[1]['headers']['Authorization'] == API_KEY
    assert os.path.exists(filepath)


@pytest.mark.parametrize('download_url', [
    'http://attacker.example/test.geojson?x=ckantest',
    'http://ckantest.attacker.example/test.geojson',
    'http://ckantest@attacker.example/test.geojson',
    'http://ckantest/dataset/some_dataset_id/resource/some_resource_id/download/test.geojson',
])
def test_api_key_is_not_sent_for_linked_resources(task_args, download_url):
    task_args['download_url'] = download_url
    task_args['url_type'] = 'api'
    filepath, mocked_get = _download(task_args, FakeResponse(download_url))

    assert mocked_get.call_args[0][0] == download_url
    assert 'headers' not in mocked_get.call_args[1]


@pytest.mark.parametrize('field, value', [
    ('dataset_id', '../../api/action'),
    ('resource_id', 'some_resource_id?x=y'),
    ('resource_id', 'some_resource_id#'),
    ('resource_id', 'some_resource_id\n'),
])
def test_invalid_ids_are_rejected_for_uploads(task_args, field, value):
    task_args[field] = value
    task = CreatePreviewTask(task_args)
    with mock.patch('importapi.tasks.create_preview.requests.get') as mocked_get:
        with pytest.raises(ValueError):
            task.download_file('testpre_layer')
    mocked_get.assert_not_called()


@pytest.mark.parametrize('content_disposition, expected_filename', [
    ('attachment; filename="../../../evil.geojson"', 'layer.geojson'),
    ('attachment; filename="/etc/cron.d/evil.kml"', 'layer.kml'),
    ('attachment; filename="test.KMZ"; size=123', 'layer.kmz'),
    ("attachment; filename*=UTF-8''test.shp.zip", 'layer.zip'),
    ('attachment; filename="../../../evil.py"', 'layer.geojson'),  # falls back to the extension from the url
])
def test_remote_filename_is_never_used_as_path(task_args, tmp_path, content_disposition, expected_filename):
    task_args['url_type'] = 'api'
    task_args['download_url'] = 'http://attacker.example/test.geojson'
    response = FakeResponse(task_args['download_url'], {'content-disposition': content_disposition})
    task = CreatePreviewTask(task_args)
    with mock.patch('importapi.tasks.create_preview.requests.get', return_value=response), \
            mock.patch('importapi.tasks.create_preview.zip_helper.Unzipper'):
        task.download_file('testpre_layer')

    download_directory = tmp_path / 'downloads' / 'testpre_layer'
    assert os.listdir(str(download_directory)) == [expected_filename]
    assert os.listdir(str(tmp_path)) == ['downloads']
    assert os.listdir(str(tmp_path / 'downloads')) == ['testpre_layer']


def test_not_accepted_extension_is_rejected(task_args):
    task_args['url_type'] = 'api'
    task_args['download_url'] = 'http://attacker.example/evil'
    response = FakeResponse(task_args['download_url'], {'content-disposition': 'attachment; filename="evil.py"'})
    with pytest.raises(ValueError):
        _download(task_args, response)

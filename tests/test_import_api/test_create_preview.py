import os
from shutil import copyfile, rmtree

import pytest

import importapi.helpers.zip as zip_helper
from importapi.tasks.create_preview import CreatePreviewTask

GEOFILE_PATH = '/srv/gislayer/tests/geofiles/{}'


@pytest.fixture(scope='module')
def args(app):
    args = {
        'verify_ckan_ssl': app.config.get('VERIFY_CKAN_SSL'),
        'ckan_server_url': app.config.get('CKAN_SERVER_URL'),
        'logging_config': app.config.get('LOGGING_CONF_FILE'),
        'download_chunk_size': app.config.get('DOWNLOAD_CHUNK_SIZE_MB'),
        'max_file_size_mb': app.config.get('MAX_FILE_SIZE_MB'),
        'timeout_sec': app.config.get('TIMEOUT_SEC'),
        'table_name_prefix': app.config.get('TABLE_NAME_PREFIX', 'testpre'),
        'ckan_api_base_url': app.config.get('CKAN_API_BASE_URL'),
        'resource_update_action': app.config.get('RESOURCE_UPDATE_ACTION'),
        'gis_api_pattern': app.config.get('GIS_API_PATTERN'),
        'hdx_user_agent': app.config.get('HDX_USER_AGENT'),
        'tmp_download_directory': app.config.get('TMP_DOWNLOAD_DIRECTORY'),

        'dataset_id': 'some_dataset_id',
        'resource_id': 'some_resource_id',
        'download_url': 'https://localhost/test.csv"',
        'url_type': 'upload',

    }
    return args


@pytest.fixture(scope='module')
def gisdb_info_in_env():

    # These should already be in the environment
    # os.environ["HDX_GISDB_HOST"] = "test_gisdb"
    # os.environ["HDX_GISDB_DB"] = "test_gisdb"
    # os.environ["HDX_GISDB_USER"] = "test_gisdb_user"
    # os.environ["HDX_GISDB_PORT"] = "5432"
    # os.environ["HDX_GISDB_PASS"] = "test_gisdb_pass"

    os.environ["HDX_GIS_API_KEY"] = "TEST_API_KEY"


    yield True

    # os.unsetenv("HDX_GISDB_HOST")
    # os.unsetenv("HDX_GISDB_DB")
    # os.unsetenv("HDX_GISDB_USER")
    # os.unsetenv("HDX_GISDB_PORT")
    # os.unsetenv("HDX_GISDB_PASS")
    os.unsetenv("HDX_GIS_API_KEY")


@pytest.fixture(scope='function')
def empty_tmp_folder():
    tmp_folder = GEOFILE_PATH.format('tmp')
    if os.path.exists(tmp_folder):
        rmtree(tmp_folder)
    os.makedirs(tmp_folder)
    return tmp_folder


def test_create_preview_geojson(args, gisdb_info_in_env):
    filename = 'test.geojson'
    filepath = GEOFILE_PATH.format(filename)

    create_preview_task, layer_metadata = _push_file_and_get_metadata(args, filepath)
    assert layer_metadata.get('bounding_box') == 'BOX(2.513573 49.529484,6.156658 51.475024)'
    assert len(layer_metadata.get('layer_fields')) == 4


def test_create_preview_kml(args, gisdb_info_in_env):
    filename = 'test.kml'
    filepath = GEOFILE_PATH.format(filename)

    create_preview_task, layer_metadata = _push_file_and_get_metadata(args, filepath)
    assert layer_metadata.get('bounding_box') == \
        'BOX(-48.8424580754653 61.049858673079,-42.2929468978678 66.2053550371775)'
    assert len(layer_metadata.get('layer_fields')) == 13


def test_create_preview_shapefile(args, gisdb_info_in_env, empty_tmp_folder):
    tmp_folder = empty_tmp_folder

    filename = 'test.shp.zip'
    create_preview_task, layer_metadata = _unzip_and_push(args, filename, tmp_folder)

    assert layer_metadata.get('bounding_box') == \
        'BOX(34.00334232 -4.40810323599999,41.81483496 4.47561039300001)'
    assert len(layer_metadata.get('layer_fields')) == 45

    create_preview_task.delete_download_directory()

    assert not os.path.exists(create_preview_task.download_directory)


def test_create_preview_shapefile_with_multilinestring_problem(args, gisdb_info_in_env, empty_tmp_folder):
    '''
    Test shapefile used from https://github.com/Esri/arcgis-runtime-samples-data, Apache 2.0 license
    '''
    tmp_folder = empty_tmp_folder

    filename = 'test2.shp.zip'
    create_preview_task, layer_metadata = _unzip_and_push(args, filename, tmp_folder)

    assert layer_metadata.get('bounding_box') == \
           'BOX(-158.090073902174 21.2775052439187,-67.7811766716047 62.1452071164588)'
    assert len(layer_metadata.get('layer_fields')) == 7

    create_preview_task.delete_download_directory()

    assert not os.path.exists(create_preview_task.download_directory)


def _unzip_and_push(args, filename, tmp_folder):
    file_to_be_pushed = _unzipping(filename, tmp_folder)
    create_preview_task, layer_metadata = _push_file_and_get_metadata(args, file_to_be_pushed)
    create_preview_task.download_directory = tmp_folder
    return create_preview_task, layer_metadata


def _unzipping(filename, tmp_folder):
    filepath = GEOFILE_PATH.format(filename)
    tmp_filepath = tmp_folder + '/' + filename
    copyfile(filepath, tmp_filepath)
    unzipper = zip_helper.Unzipper(tmp_filepath)
    unzipper.unzip()
    file_to_be_pushed = unzipper.find_layer_file()
    return file_to_be_pushed


def _push_file_and_get_metadata(args, filepath):
    create_preview_task = CreatePreviewTask(args)
    layer_id = 'test_resource'
    create_preview_task.push_file_to_postgis(filepath, layer_id)
    layer_metadata = create_preview_task.fetch_layer_metadata_from_db(layer_id)
    return create_preview_task, layer_metadata

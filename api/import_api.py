import os
import time
import shutil

import flask
import requests
import urlparse
import subprocess
import logging
import hashlib

import api.helpers.zip as zip
import api.exceptions.exceptions as exceptions

Flask = flask.Flask
jsonify = flask.jsonify
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response

logger = logging.getLogger(__name__)

app = flask.current_app

import_api = Blueprint('import_api', __name__)


@import_api.route('/api/add-layer/dataset/<string:dataset_id>/resource/<string:resource_id>', methods=['GET'])
def add_layer(dataset_id, resource_id):
    data_dict = {
        'success': 'true',
        'message': 'Import successful',
        'layer_id': 'None',
        'error_type': 'None',
        'error_class': 'None'
    }
    # url = 'https://data.hdx.rwlabs.org/dataset/lsib-simplified-shoreline/resource_download/d20c3101-7585-4145-a579-6acec7aadf61'
    try:
        download_url = _get_download_url(request)
        layer_id = generate_layer_id(dataset_id, download_url)
        data_dict['layer_id'] = layer_id
        file_to_be_pushed = download_file(layer_id, download_url)
        push_file_to_postgis(file_to_be_pushed, layer_id)
        notify_gis_server(layer_id)
    except Exception, e:
        data_dict['success'] = False
        data_dict['message'] = str(e)
        data_dict['error_class'] = type(e).__name__
        try:
            data_dict['type'] = e.type
        except AttributeError,e:
            data_dict['type'] = 'unknown'

    return jsonify(data_dict)


def download_file(layer_id, url):
    max_file_size = int(app.config.get('MAX_FILE_SIZE_MB','1')) * 1024 * 1024
    timeout = int (app.config.get('TIMEOUT_SEC', '1'))
    chunk_size = 1024*1024  # 1 MB

    # timeout is 1 sec
    r = requests.get(url, stream=True, timeout=1)
    r.raise_for_status()

    content_length = r.headers.get('Content-Length')
    if not content_length:
        logger.warning('Content length not specified in HTTP response for url: '.format(url))
    elif int(content_length) > max_file_size:
        raise exceptions.FileTooLargeException('response too large')

    size = 0
    start = time.time()
    dir = '/tmp/' + layer_id
    filepath = dir + '/' + _get_filename(r, url)
    extension = os.path.splitext(filepath)[1]

    file_to_be_pushed = None

    _create_download_dir(dir)

    with open(filepath, "wb") as fh:
        try:
            for chunk in r.iter_content(chunk_size):
                if time.time() - start > timeout:
                    logger.error('Timeout while downloading file {}'.format(url))
                    raise exceptions.TimeoutException('timeout reached')

                size += len(chunk)
                if size > max_file_size:
                    logger.error('Size exceeded while downloading file {}'.format(url))
                    raise exceptions.FileTooLargeException('response too large')

                fh.write(chunk)
            file_to_be_pushed = filepath
        except Exception as e:
                logger.error('Exception occured while downloading file {}: {}'.format(filepath, str(e)))
                raise e
        finally:
            r.close()

    if extension == '.zip':
        zip_helper = zip.Unzipper(filepath)
        zip_helper.unzip()
        file_to_be_pushed = zip_helper.find_layer_file()

    logger.info('File {} will be pushed to PostGIS'.format(file_to_be_pushed))
    return file_to_be_pushed



def _create_download_dir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
    except Exception as e:
        msg = 'A problem occured while creating folder {}: {}'.format(dir, str(e))
        logger.error(msg)
        raise exceptions.FolderCreationException(msg, [e])


def _get_filename(response, url):
    header_filename = response.headers.get('content-disposition')
    if header_filename:
        file_name = header_filename.split("filename=")[-1]
        return file_name.replace('"', '')
    else:
        split_url = urlparse.urlsplit(url)
        if split_url.path:
            file_name = os.path.basename(split_url.path)
            if file_name.split(".")[-1].lower() in ['json', 'geojson', 'zip']:
                return file_name
    raise ValueError('Filename could not be found')


def push_file_to_postgis(filepath, resource_id, additional_params=None):
    db_host = app.config.get('DB_HOST','db')
    db_name = app.config.get('DB_NAME','gis')
    db_user = app.config.get('DB_USER','ckan')

    execute = [
        'ogr2ogr',
        '-f',
        '"PostgreSQL"',
        'PG:host={} dbname={} user={}'.format(db_host, db_name, db_user),
        '{}'.format(filepath),
        '-nln',
        resource_id,
        '-overwrite',
        '-lco',
        'OVERWRITE=YES',
        '-fieldTypeToString',
        'Real'
    ]
    if additional_params:
        execute = execute + additional_params
    try:
        output = subprocess.check_output(execute, stderr=subprocess.STDOUT)
        logger.info('Pushed {} successfully to table {}'.format(filepath, resource_id))
    except subprocess.CalledProcessError, e:
        pass
        logger.warning(str(e))
        output = e.output
        logger.debug('ogr2ogr output: {}'.format(output))

        # avoid infinte cycles
        if not additional_params and 'does not match column type (Polygon)' in output:
            logger.debug('Geometry type problem. Trying to force MultiPolygon geometry for file {}'.format(filepath))
            push_file_to_postgis(filepath, resource_id, ['-nlt','MultiPolygon'])
        elif not additional_params and 'does not match column type (LineString)' in output:
            logger.debug('Geometry type problem. Trying to force MultiLineString geometry for file {}'.format(filepath))
            push_file_to_postgis(filepath, resource_id, ['-nlt','MultiLineString'])
        else:
            raise exceptions.PushingToPostgisException('Problem while trying to push data to postgis')



def notify_gis_server(resource_id):
    gis_api_url = app.config.get('GIS_API_PATTERN').format(table_name=resource_id)
    r = requests.get(gis_api_url)
    r.raise_for_status()
    r.close()


def generate_layer_id(dataset_id, url):
    dataset_prefix = ''.join(i if i.isalnum() else '_' for i in dataset_id)
    layer_id = "{}_{}".format(dataset_prefix, hashlib.md5(url).hexdigest())
    return layer_id


def _get_download_url(request):
    try:
        return request.args['resource_download_url']
    except Exception, e:
        raise exceptions.MissingUrlException("Url missing or has a problem", [e])

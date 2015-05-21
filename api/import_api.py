import os
import time
import shutil

import flask
import requests
import urlparse
import subprocess

import api.helpers.zip as zip

Flask = flask.Flask
jsonify = flask.jsonify
request = flask.request
Blueprint = flask.Blueprint

app = flask.current_app

import_api = Blueprint('import_api', __name__)


@import_api.route('/api/add-layer/<string:dataset_id>/<string:resource_id>', methods=['GET'])
def add_layer(dataset_id, resource_id):
    download_url = request.args.get('resource_download_url', '')
    data_dict = {
        'success': 'true',
        'message': 'Import successful',
        'error_type': 'Timeout',
    }
    # url = 'https://data.hdx.rwlabs.org/dataset/lsib-simplified-shoreline/resource_download/d20c3101-7585-4145-a579-6acec7aadf61'
    file_to_be_pushed = download_file(resource_id, download_url)
    push_file_to_postgis(file_to_be_pushed, resource_id)
    notify_gis_server(resource_id)

    return jsonify(data_dict)


def download_file(resource_id, url):
    max_file_size = int(app.config.get('MAX_FILE_SIZE_MB','1')) * 1024 * 1024
    timeout = int (app.config.get('TIMEOUT_SEC', '1'))
    chunk_size = 1024*1024  # 1 MB

    # timeout is 1 sec
    r = requests.get(url, stream=True, timeout=1)
    r.raise_for_status()

    content_length = r.headers.get('Content-Length')
    if not content_length:
        app.logger.warning('Content length not specified in HTTP response for url: '.format(url))
    elif int(content_length) > max_file_size:
        raise ValueError('response too large')

    size = 0
    start = time.time()
    dir = '/tmp/' + resource_id
    filepath = dir + '/' + _get_filename(r, url)
    extension = os.path.splitext(filepath)[1]

    file_to_be_pushed = None
    if _create_download_dir(dir):
        with open(filepath, "wb") as fh:
            try:
                for chunk in r.iter_content(chunk_size):
                    if time.time() - start > timeout:
                        raise ValueError('timeout reached')

                    size += len(chunk)
                    if size > max_file_size:
                        raise ValueError('response too large')

                    fh.write(chunk)
                file_to_be_pushed = filepath
            except Exception as e:
                    app.logger.error('Exception occured while downloading file {}: {}'.format(filepath, str(e)))
                    raise e
            finally:
                r.close()

        if extension == '.zip':
            zip_helper = zip.Unzipper(filepath)
            zip_helper.unzip()
            file_to_be_pushed = zip_helper.find_layer_file()

        app.logger.info('File {} will be pushed to PostGIS'.format(file_to_be_pushed))
        return file_to_be_pushed


def _create_download_dir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        return True
    except Exception as e:
        app.logger.error('A problem occured while creating folder {}: {}'.format(dir, str(e)))
        return False


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


def push_file_to_postgis(filepath, resource_id):
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
        '-fieldTypeToString',
        'Real'
    ]
    try:
        output = subprocess.check_output(execute, stderr=subprocess.STDOUT)
        app.logger.info('Pushed {} successfully to table {}'.format(filepath, resource_id))
    except subprocess.CalledProcessError, e:
        pass
        app.logger.warning(str(e))
        output = e.output

    app.logger.debug('ogr2ogr output: {}'.format(output))


def notify_gis_server(resource_id):
    gis_api_url = app.config.get('GIS_API_PATTERN').format(table_name=resource_id)
    r = requests.get(gis_api_url)
    r.raise_for_status()
    r.close()
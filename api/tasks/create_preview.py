import os
import logging
import logging.config
import shutil
import subprocess
import time
import urlparse
import requests
import json
import api.exceptions.exceptions as exceptions
import api.helpers.zip as zip_helper

logger = logging.getLogger(__name__)


def create_preview_task(task_arguments):
    task = CreatePreviewTask(task_arguments)
    return task.process()


class CreatePreviewTask(object):
    def __init__(self, args):
        logging.config.fileConfig(args['logging_config'])

        self.dataset_id = args['dataset_id']
        self.resource_id = args['resource_id']
        self.download_url = args['download_url']
        self.max_file_size = args['max_file_size_mb']
        self.timeout = args['timeout_sec']
        self.api_key = args['ckan_api_key']
        self.resource_update_api = args['resource_update_api']
        self.gis_api_pattern = args['gis_api_pattern']
        self.table_prefix = args['table_name_prefix']

        self.db_host = args['db_host']
        self.db_name = args['db_name']
        self.db_user = args['db_user']

    def process(self):
        logger.info("In create_preview_task for {}, {}, {}".format(self.dataset_id, self.resource_id, self.download_url))
        data_dict = {
            'state': 'success',
            'message': 'Import successful',
            'layer_id': 'None',
            'error_type': 'None',
            'error_class': 'None'
        }

        try:

            layer_id = self.generate_layer_id()
            data_dict['layer_id'] = layer_id
            file_to_be_pushed = self.download_file(layer_id)
            self.push_file_to_postgis(file_to_be_pushed, layer_id)
            bounding_box = self.fetch_bounding_box(layer_id)
            data_dict['bounding_box'] = bounding_box
            self.notify_gis_server(layer_id)
        except Exception, e:
            data_dict['state'] = 'failure'
            data_dict['message'] = str(e)
            data_dict['error_class'] = type(e).__name__
            try:
                data_dict['type'] = e.type
            except AttributeError:
                data_dict['type'] = 'unknown'

        self.push_information_back_to_ckan(data_dict)

    def download_file(self, layer_id):

        chunk_size = 1024*1024  # 1 MB

        # timeout is 1 sec
        r = requests.get(self.download_url, stream=True, timeout=1, headers={"Authorization": self.api_key},)
        r.raise_for_status()

        content_length = r.headers.get('Content-Length')
        if not content_length:
            logger.warning('Content length not specified in HTTP response for url: '.format(self.download_url))
        elif int(content_length) > self.max_file_size:
            raise exceptions.FileTooLargeException('response too large')

        size = 0
        start = time.time()
        directory = '/tmp/' + layer_id
        filepath = directory + '/' + self._get_filename(r)
        extension = os.path.splitext(filepath)[1]

        file_to_be_pushed = None

        self._create_download_dir(directory)

        with open(filepath, "wb") as fh:
            try:
                for chunk in r.iter_content(chunk_size):
                    if time.time() - start > self.timeout:
                        logger.error('Timeout while downloading file {}'.format(self.download_url))
                        raise exceptions.TimeoutException('timeout reached')

                    size += len(chunk)
                    if size > self.max_file_size:
                        logger.error('Size exceeded while downloading file {}'.format(self.download_url))
                        raise exceptions.FileTooLargeException('response too large')

                    fh.write(chunk)
                file_to_be_pushed = filepath
            except Exception as e:
                    logger.error('Exception occured while downloading file {}: {}'.format(filepath, str(e)))
                    raise e
            finally:
                r.close()

        if extension == '.zip':
            unzipper = zip_helper.Unzipper(filepath)
            unzipper.unzip()
            file_to_be_pushed = unzipper.find_layer_file()

        logger.info('File {} will be pushed to PostGIS'.format(file_to_be_pushed))
        return file_to_be_pushed

    def _create_download_dir(self, directory):
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)
        except Exception as e:
            msg = 'A problem occured while creating folder {}: {}'.format(directory, str(e))
            logger.error(msg)
            raise exceptions.FolderCreationException(msg, [e])

    def _get_filename(self, response):
        header_filename = response.headers.get('content-disposition')
        if header_filename:
            file_name = header_filename.split("filename=")[-1]
            return file_name.replace('"', '')
        else:
            split_url = urlparse.urlsplit(self.download_url)
            if split_url.path:
                file_name = os.path.basename(split_url.path)
                if file_name.split(".")[-1].lower() in ['json', 'geojson', 'zip']:
                    return file_name
        raise ValueError('Filename could not be found')

    def push_file_to_postgis(self, filepath, resource_id, additional_params=None):

        execute = [
            'ogr2ogr',
            '-f',
            '"PostgreSQL"',
            'PG:host={} dbname={} user={}'.format(self.db_host, self.db_name, self.db_user),
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
            logger.warning(str(e))
            output = e.output
            logger.debug('ogr2ogr output: {}'.format(output))

            # avoid infinte cycles
            if not additional_params and 'does not match column type (Polygon)' in output:
                logger.debug(
                    'Geometry type problem. Trying to force MultiPolygon geometry for file {}'.format(filepath))
                self.push_file_to_postgis(filepath, resource_id, ['-nlt', 'MultiPolygon'])
            elif not additional_params and 'does not match column type (LineString)' in output:
                logger.debug(
                    'Geometry type problem. Trying to force MultiLineString geometry for file {}'.format(filepath))
                self.push_file_to_postgis(filepath, resource_id, ['-nlt', 'MultiLineString'])
            else:
                raise exceptions.PushingToPostgisException('Problem while trying to push data to postgis')

    def fetch_bounding_box(self, resource_id):

        sql_query = 'select ST_Extent(wkb_geometry) as table_extent from {}'.format(resource_id)

        execute = [
            'psql',
            '-U',
            self.db_user,
            '-h',
            self.db_host,
            '-c',
            sql_query,
            '-t', # turn off table header and row count
            self.db_name
        ]

        try:
            logger.debug('Starting to fetch bounding box for resource {}'.format(resource_id))
            output = subprocess.check_output(execute, stderr=subprocess.STDOUT)
            output = output.strip()
            logger.info('Fetched bounding box. "{}" for resource {}'.format(output, resource_id))
            return output
        except subprocess.CalledProcessError, e:
            logger.warning(str(e))
            output = e.output
            raise exceptions.FetchBoundingBoxException(output)

    def notify_gis_server(self, resource_id):
        gis_api_url = self.gis_api_pattern.format(table_name=resource_id)
        r = requests.get(gis_api_url)
        r.raise_for_status()
        r.close()

    def push_information_back_to_ckan(self, shape_info_dict):

        if self.resource_update_api and self.api_key:
            try:
                shape_info_json = json.dumps(shape_info_dict)
                data_json = json.dumps({'id': self.resource_id, 'shape_info': shape_info_json})
                logger.debug('Pushing following information for resource {}: {}'.format(self.resource_id, data_json))
                r = requests.post(self.resource_update_api,
                                  data=data_json,
                                  headers={"Authorization": self.api_key, 'content-type': 'application/json'},
                                  verify=False)
                logger.info('Pushed back shape_info for resource {}. Result is: {}'.format(self.resource_id, r.json()))
            except Exception, e:
                logger.error(str(e))
        else:
            logger.error(
                'Update url or api key missing when pushing back shape info for resource {}'.format(self.resource_id))
            raise exceptions.WrongConfigurationException('Either resource update url or api key missing')

    def generate_layer_id(self):
        # dataset_prefix = ''.join(i if i.isalnum() else '_' for i in dataset_id[0:10])

        main_part = ''.join(i if i.isalnum() else '_' for i in self.resource_id)
        layer_id = "{}_{}".format(self.table_prefix, main_part)
        return layer_id

import json
import logging
import os
import shutil
import subprocess
import time

import future.moves.urllib.parse as urlparse
import requests

import helpers.db_helper as db_helper
import importapi.exceptions.exceptions as exceptions
import importapi.helpers.problem_solver as problem_solver
import importapi.helpers.zip as zip_helper

logger = logging.getLogger(__name__)

accepted_extensions = ['json', 'geojson', 'zip', 'kml', 'kmz']


def create_preview_task(task_arguments):
    task = CreatePreviewTask(task_arguments)
    return task.process()


class CreatePreviewTask(object):
    def __init__(self, args):
        self.dataset_id = args['dataset_id']
        self.resource_id = args['resource_id']
        self.download_url = args['download_url']
        self.verify_ckan_ssl = args['verify_ckan_ssl']
        self.ckan_server_url = args['ckan_server_url']
        self.url_type = args['url_type']
        self.download_chunk_size = args['download_chunk_size']
        self.max_file_size = args['max_file_size_mb']
        self.timeout = args['timeout_sec']
        # self.worker_timeout = args['worker_timeout_sec']

        self.resource_update_api = '{}/{}'.format(args['ckan_api_base_url'], args['resource_update_action'])
        self.gis_api_pattern = args['gis_api_pattern']
        self.table_prefix = args['table_name_prefix']

        self.db_host = os.getenv('HDX_GISDB_ADDR', 'gisdb')
        self.db_name = os.getenv('HDX_GISDB_DB', 'gis')
        self.db_user = os.getenv('HDX_GISDB_USER', 'gis')
        self.db_port = os.getenv('HDX_GISDB_PORT', '5432')
        self.db_pass = os.getenv('HDX_GISDB_PASS')

        self.api_key = os.getenv('HDX_GIS_API_KEY')

        self.tmp_download_directory = args['tmp_download_directory']
        self.download_directory = None

        self.headers_for_ckan = {
            'User-Agent': args['hdx_user_agent'],
            'Authorization': self.api_key
        }

    def process(self):
        logger.info(
            "In create_preview_task for {}, {}, {}".format(self.dataset_id, self.resource_id, self.download_url))
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
            layer_metadata = self.fetch_layer_metadata_from_db(layer_id)
            data_dict.update(layer_metadata)
            # self.notify_gis_server(layer_id)
        except Exception as e:
            data_dict['state'] = 'failure'
            data_dict['message'] = str(e)
            data_dict['error_class'] = type(e).__name__
            try:
                data_dict['type'] = e.type
            except AttributeError:
                data_dict['type'] = 'unknown'




        self.push_information_back_to_ckan(data_dict)
        self.delete_download_directory()

    def download_file(self, layer_id):

        # timeout for both setting up a connection and reading first byte is 12 sec
        r = None
        if self.ckan_server_url in self.download_url:  # if URL is on the CKAN site
            r = requests.get(self.download_url, stream=True, timeout=12, verify=self.verify_ckan_ssl,
                             headers=self.headers_for_ckan)
        else:
            r = requests.get(self.download_url, stream=True, timeout=12)
        r.raise_for_status()

        content_length = r.headers.get('Content-Length')
        if not content_length:
            logger.warning('Content length not specified in HTTP response for url: '.format(self.download_url))
        elif int(content_length) > self.max_file_size:
            raise exceptions.FileTooLargeException('response too large')

        size = 0
        start = time.time()
        directory = '{}/{}'.format(self.tmp_download_directory, layer_id)
        # directory = '/tmp/' + layer_id
        filepath = directory + '/' + self._get_filename(r)
        extension = os.path.splitext(filepath)[1]

        file_to_be_pushed = None

        self._create_download_dir(directory)
        self.download_directory = directory

        logger.info('Starting to download dataset {} resource {} from URL {} to filepath {}'
                    .format(self.dataset_id, self.resource_id, self.download_url, filepath))

        with open(filepath, "wb") as fh:
            try:
                for chunk in r.iter_content(self.download_chunk_size):

                    size += len(chunk)
                    if size > self.max_file_size:
                        logger.error('Size exceeded while downloading file {}'.format(self.download_url))
                        raise exceptions.FileTooLargeException('response too large')

                    passed_time = time.time() - start

                    if passed_time > self.timeout:
                        logger.error('Timeout while downloading file {}'.format(self.download_url))
                        raise exceptions.TimeoutException('timeout reached')
                    else:
                        logger.debug('Passed time {} ; Size {} (for dataset {} and resource {})'.
                                     format(passed_time, size, self.dataset_id, self.resource_id))
                    fh.write(chunk)
                file_to_be_pushed = filepath
                logger.info('Finished downloading dataset {} resource {} to filepath {}'
                            .format(self.dataset_id, self.resource_id, filepath))
            except Exception as e:
                logger.error('Exception occured while downloading file {}: {}'.format(filepath, str(e)))
                raise e
            finally:
                r.close()

        if extension and extension.lower() == '.zip':
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
                if file_name.split(".")[-1].lower() in accepted_extensions:
                    return file_name
        raise ValueError('CKAN resource filename could not be deduced')

    def push_file_to_postgis(self, filepath, resource_id, solution=None):

        execute = [
            'ogr2ogr',
            '--config',
            'PG_USE_COPY',
            'NO',
            '-f',
            '"PostgreSQL"',
            'PG:host={} dbname={} port={} user={} password={}'.format(self.db_host, self.db_name, self.db_port, self.db_user, self.db_pass),
            '{}'.format(filepath),
            '-nln',
            resource_id,
            '-overwrite',
            '-lco',
            'OVERWRITE=YES',
            '-fieldTypeToString',
            'Real',
            '-t_srs',
            'EPSG:4326'

        ]
        if solution:
            additional_params = []
            for key, value in solution.get_ogr_items():
                additional_params.append(key)
                additional_params.append(value)
            execute = execute + additional_params
        try:
            if solution and solution.has_env_keys():
                my_env = os.environ.copy()
                my_env.update({key: value for key, value in solution.get_env_items()})
                output = subprocess.check_output(execute, stderr=subprocess.STDOUT, env=my_env)
            else:
                # first time tryin to improt this file
                output = subprocess.check_output(execute, stderr=subprocess.STDOUT)
            logger.info('Pushed to POSTGIS {} successfully to table {}'.format(filepath, resource_id))
        except subprocess.CalledProcessError as e:
            logger.warning(str(e))
            output = e.output
            output = output.decode('utf-8', 'ignore') if output else ''
            logger.debug('ogr2ogr output: {}'.format(output))

            current_version = solution.version if solution else 0
            solver = problem_solver.ProblemSolver(filepath, solution)
            new_solution = solver.find_solution(output)

            if current_version < new_solution.version:
                self.push_file_to_postgis(filepath, resource_id, new_solution)
            else:
                logger.info('Gave up on pushing to POSTGIS {}'.format(filepath))
                raise exceptions.PushingToPostgisException('Problem during ogr2ogr import to postgis')


                # avoid infinte cycles
                # if not additional_params and 'does not match column type (Polygon)' in output:
                #     logger.debug(
                #         'Geometry type problem. Trying to force MultiPolygon geometry for file {}'.format(filepath))
                #     self.push_file_to_postgis(filepath, resource_id, ['-nlt', 'MultiPolygon'], additional_env)
                # elif not additional_params and 'does not match column type (LineString)' in output:
                #     logger.debug(
                #         'Geometry type problem. Trying to force MultiLineString geometry for file {}'.format(filepath))
                #     self.push_file_to_postgis(filepath, resource_id, ['-nlt', 'MultiLineString'], additional_env)
                # elif not additional_params and 'Can\'t transform coordinates, source layer has no' in output:
                #     logger.debug(
                #         'Source SRS missing. Trying again with EPSG:4326 for file {}'.format(filepath))
                #     self.push_file_to_postgis(filepath, resource_id, ['-s_srs', 'EPSG:4326'], additional_env)
                # elif not additional_env and 'invalid byte sequence for encoding' in output:
                #     logger.debug(
                #         'Character encoding problem. Trying with PGCLIENTENCODING=latin1 for file {}'.format(filepath))
                #     self.push_file_to_postgis(filepath, resource_id, additional_params, {'PGCLIENTENCODING': 'latin1'})
                # else:
                #     raise exceptions.PushingToPostgisException('Problem during ogr2ogr import to postgis')

    def fetch_layer_metadata_from_db(self, resource_id):
        logger.debug('Starting to fetch bounding box and fields for resource {}'.format(resource_id))

        with db_helper.DbHelper(self.db_host, self.db_port, self.db_name, self.db_user, self.db_pass) as dbh:
            bounding_box = dbh.fetch_one_item(
                'select ST_Extent(wkb_geometry)::text as table_extent from {}'.format(resource_id), None)
            logger.info('Fetched bounding box: "{}" for resource {}'.format(bounding_box, resource_id))

            f_sql = "select column_name as field_name, data_type from information_schema.columns where table_name=%s"
            layer_fields = dbh.fetch_dictionary(f_sql, (resource_id,))

            logger.info('Fetched layer fields: "{}" for resource {}'.format(str(layer_fields), resource_id))

        if not bounding_box:
            raise exceptions.FetchLayerMetadataException('Bounding box was not retrieved ')
        if not layer_fields:
            raise exceptions.FetchLayerMetadataException('Layer fields were not retrieved ')

        return {
            'bounding_box': bounding_box,
            'layer_fields': layer_fields
        }

    # def notify_gis_server(self, resource_id):
    #     gis_api_url = self.gis_api_pattern.format(table_name=resource_id)
    #     r = requests.get(gis_api_url, verify=self.verify_ckan_ssl)
    #     r.raise_for_status()
    #     r.close()

    def push_information_back_to_ckan(self, shape_info_dict):

        if self.resource_update_api and self.api_key:
            try:
                shape_info_json = json.dumps(shape_info_dict)
                data_json = json.dumps({
                    'id': self.resource_id,
                    'shape_info': shape_info_json,
                    'batch_mode': 'KEEP_OLD'
                })
                logger.debug('Before pushing to CKAN following information for resource {}: {}'.format(self.resource_id,
                                                                                                       data_json))
                headers = {'content-type': 'application/json'}
                headers.update(self.headers_for_ckan)
                r = requests.post(self.resource_update_api,
                                  data=data_json,
                                  headers=headers,
                                  verify=self.verify_ckan_ssl)
                logger.info(
                    'Pushed to CKAN shape_info for resource {}. Result is: {}'.format(self.resource_id, r.json()))
            except Exception as e:
                logger.error(str(e))
        else:
            logger.error(
                'Update url or importapi key missing when pushing to CKAN shape info for resource {}'.format(
                    self.resource_id))
            raise exceptions.WrongConfigurationException('Either CKAN resource update url or importapi key missing')

    def generate_layer_id(self):
        # dataset_prefix = ''.join(i if i.isalnum() else '_' for i in dataset_id[0:10])

        main_part = ''.join(i if i.isalnum() else '_' for i in self.resource_id)
        layer_id = "{}_{}".format(self.table_prefix, main_part)
        return layer_id

    def delete_download_directory(self):
        if self.download_directory and os.path.exists(self.download_directory):
            try:
                logger.info('Deleting folder {}'.format(self.download_directory))
                shutil.rmtree(self.download_directory)
            except Exception as e:
                logger.error(str(e))
        else:
            logger.warning('Not deleting directory for resource id {} because download dir does not exist'.format(
                self.resource_id))

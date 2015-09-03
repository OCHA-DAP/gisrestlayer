import logging
import requests
import sets

import helpers.db_helper as db_helper
import deleteapi.exceptions.exceptions as exceptions

logger = logging.getLogger(__name__)

class LayersCleaner(object):
    def __init__(self, db_params, ckan_params, dry_run=True):
        self.db_host = db_params['db_host']
        self.db_port = db_params['db_port']
        self.db_name = db_params['db_name']
        self.db_user = db_params['db_user']
        self.db_pass = db_params['db_pass']
        self.table_name_prefix = db_params['table_name_prefix']

        self.resource_id_list_api = ckan_params['resource_id_list_api']
        self.api_key = ckan_params['ckan_api_key']
        self.verify_ckan_ssl = ckan_params['verify_ckan_ssl']

        self.dry_run = dry_run

    def process(self):
        data_dict = {
            'state': 'None',
            'message': 'None',
            'count':'None',
            'items': [],
            'dry-run': self.dry_run,
            'error_type': 'None',
            'error_class': 'None'
        }
        try:
            self._fetch_list_of_layers()
            self._find_deleted_layers()

            m = 'Deleting {} layers from postgis out of {}. A total of {} resources was found on CKAN'.format(
                len(self.deletable_layer_ids), len(self.layer_ids), len(self.resource_list))
            data_dict['message'] = m
            data_dict['count'] = len(self.deletable_layer_ids)
            data_dict['items'] = list(self.deletable_layer_ids)
        except Exception as e:
            data_dict['state'] = 'failure'
            data_dict['message'] = str(e)
            data_dict['error_class'] = type(e).__name__
            try:
                data_dict['type'] = e.type
            except AttributeError:
                data_dict['type'] = 'unknown'

        return data_dict

    def _fetch_list_of_layers(self):
        logger.debug('Before fetching layer ids from postgis')
        try:
            with db_helper.DbHelper(self.db_host, self.db_port, self.db_name, self.db_user, self.db_pass) as dbh:
                table_starts_with = '{}_%'.format(self.table_name_prefix)
                query = '''SELECT table_name FROM information_schema.tables
                            WHERE table_schema='public' AND table_name LIKE %s ORDER BY table_name;'''
                tables = dbh.fetch_list(query, (table_starts_with,))
                self.layer_ids = [table[len(self.table_name_prefix)+1:].replace('_', '-') for table in tables]
                logger.info('Fetched {} layer ids'.format(len(self.layer_ids)))
        except Exception as e:
            msg = 'Problem while fetching layer list'
            logger.error(msg)
            raise exceptions.FetchLayerIdsException(msg, [e])


    def _find_deleted_layers(self):
        logger.debug('Before fetching resource ids from CKAN')
        r = requests.get(self.resource_id_list_api,
                          headers={"Authorization": self.api_key},
                          verify=self.verify_ckan_ssl)
        r.raise_for_status()

        response = r.json()

        if 'result' in response and len(response['result']) > 1:
            self.resource_list = response['result']
            length = len(self.resource_list)
            logger.debug('Found {} resource. Starting search...'.format(length) )
            self.deletable_layer_ids = set(self.layer_ids)
            for idx,resource in enumerate(self.resource_list):
                if (idx+1)%1000 == 0:
                    logger.debug('Progress: {}/{}'.format(idx+1, length))
                self.deletable_layer_ids.discard(resource)
        else:
            msg = 'Seems like the ckan list of resources is not correct'
            logger.error(msg)
            raise exceptions.CkanInfoException(msg)


import logging
import json
import requests
import os
import datetime
import filestructurecheckapi.exceptions.exceptions as exceptions
import filestructurecheckapi.helpers.detect_changes as dc
import importapi.exceptions.exceptions as import_api_exceptions

logger = logging.getLogger(__name__)


def fs_check_task(task_arguments):
    task = FSCheckTask(task_arguments)
    return task.process()


class FSCheckTask(object):
    def __init__(self, args):
        self.dataset_id = args.get('dataset_id')
        self.resource_id = args.get('resource_id')
        # self.download_url = args.get('download_url')
        self.verify_ckan_ssl = args.get('verify_ckan_ssl')
        self.ckan_server_url = args.get('ckan_server_url')
        # self.url_type = args.get('url_type')
        self.timeout = args.get('timeout_sec')
        self.hxl_proxy_source_info_url = args.get('hxl_proxy_source_info_url')
        self.fs_check_info = args.get('fs_check_info')
        # TODO remove testing api_key
        self.api_key = os.getenv('HDX_FSCHECK_API_KEY', os.getenv('HDX_GIS_API_KEY'))
        self.resource_update_api = '{}/{}'.format(args['ckan_api_base_url'], args['resource_update_action'])

        self.headers_for_ckan = {
            'User-Agent': args['hdx_user_agent'],
            'Authorization': self.api_key
        }

    def process(self):
        logger.info(
            "In fs_check for {}, {}".format(self.dataset_id, self.resource_id))
        try:
            # hxl_proxy_source_info_url = self.hxl_proxy_source_info_url
            # TODO uncomment next line and comment text line
            response = requests.get(self.hxl_proxy_source_info_url, allow_redirects=True)
            # DEBUG - for local env
            # response = requests.get(
            #     'https://data.humdata.org/hxlproxy/api/source-info?url=https://data.humdata.org/dataset/6c4c69cf-8ca0-4bfc-8c46-73cdb18812d5/resource/cfe1321e-89ce-43f3-b067-6da4bbb3ca80/download/somalia-2022-post-gu-total-acute-malnutrition-burden-and-prevalence-for-aug-2022-to-jul-2023-by.xlsx',
            #     allow_redirects=True)
            logger.info("task done")
            data_dict = json.loads(response.text)
            sheet_changes = self.process_fs_check_info_changes(data_dict)
            self.push_information_back_to_ckan(data_dict, sheet_changes)
            return response
        except Exception as ex:
            logger.error(ex)
            raise exceptions.HXLProxyException('hxl proxy error/exception')

    def push_information_back_to_ckan(self, fs_check_info_dict, sheet_changes):

        if self.resource_update_api and self.api_key:
            try:
                fs_check_info_json = json.dumps(fs_check_info_dict)
                data_json = json.dumps({
                    'id': self.resource_id,
                    'package_id': self.dataset_id,
                    'key': 'fs_check_info',
                    'value': {
                        "state": "success",
                        "message": "File structure check completed",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "sheet_changes": sheet_changes,
                        "hxl_proxy_response": fs_check_info_dict
                    }
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
                    'Pushed to CKAN fs_check_info for resource {}. Result is: {}'.format(self.resource_id, r.json()))
            except Exception as e:
                logger.error(str(e))
        else:
            logger.error(
                'Update url or import api key missing when pushing to CKAN fs_check info for resource {}'.format(
                    self.resource_id))
            raise import_api_exceptions.WrongConfigurationException('Either CKAN resource update url or import api key missing')

    def process_fs_check_info_changes(self, data_dict):
        sheet_changes = []
        if self.fs_check_info:
            _fs_check_info = json.loads(self.fs_check_info)
            success_item_list = [item for item in _fs_check_info if item.get('state') == 'success']
            if success_item_list and len(success_item_list)>=1:
                last_success_item = success_item_list[-1]
                current_item = {
                    'state': 'success',
                    'message': '',
                    'timestamp':'',
                    'hxl_proxy_response': data_dict
                }
                file_structure_event_list = dc.detect_file_structure_changes( current_item, last_success_item)
                for fse in file_structure_event_list:
                    sheet_changes.append({
                        'name':fse.sheet_id,
                        'event_type':fse.event_type,
                        'changed_fields':fse.changed_fields or '',
                    })

        return sheet_changes

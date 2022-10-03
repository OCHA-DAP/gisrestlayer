import logging
import json
import requests
import os
import datetime
import filestructurecheckapi.exceptions.exceptions as exceptions
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
        # TODO remove testing api_key
        self.api_key = os.getenv('HDX_GIS_API_KEY')
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
            # response = requests.get(self.hxl_proxy_source_info_url, allow_redirects=True)
            response = requests.get(
                'https://data.humdata.org/hxlproxy/api/source-info?url=https://dev.data-humdata-org.ahconu.org/dataset/aeb56cc0-d7a6-4518-9621-a562e2e4edbc/resource/ca94cac7-0462-4ea2-b5ba-5510518b0a6c/download/test.xlsx',
                allow_redirects=True)
            logger.info("task done")
            data_dict = json.loads(response.text)
            self.push_information_back_to_ckan(data_dict)
            return response
        except Exception as ex:
            logger.error(ex)
            raise exceptions.HXLProxyException('hxl proxy error/exception')

    def push_information_back_to_ckan(self, fs_check_info_dict):

        if self.resource_update_api and self.api_key:
            try:
                fs_check_info_json = json.dumps(fs_check_info_dict)
                data_json = json.dumps({
                    'id': self.resource_id,
                    'package_id': self.dataset_id,
                    'key': 'fs_check_info',
                    'value': {
                        "state": "success",
                        "message": "Hxl Proxy data received successfully",
                        "timestamp": datetime.datetime.now().isoformat(),
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
                'Update url or importapi key missing when pushing to CKAN fs_check info for resource {}'.format(
                    self.resource_id))
            raise import_api_exceptions.WrongConfigurationException('Either CKAN resource update url or importapi key missing')

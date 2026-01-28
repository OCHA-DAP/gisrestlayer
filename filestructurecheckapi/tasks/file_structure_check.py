import logging
import json
from typing import List, Dict, Any, Optional
import requests
import os
import datetime
from requests import Response
import filestructurecheckapi.exceptions.exceptions as exceptions
import filestructurecheckapi.helpers.detect_changes as dc
import importapi.exceptions.exceptions as import_api_exceptions

from json import JSONDecodeError

logger = logging.getLogger(__name__)


def fs_check_task(task_arguments):
    task = FSCheckTask(task_arguments)
    return task.process()

STATE_SUCCESS = "success"
STATE_ERROR = "error"
KEY_FS_CHECK_INFO = "fs_check_info"

class FSCheckTask(object):

    def __init__(self, args: dict) -> None:
        self.dataset_id = args.get('dataset_id')
        self.resource_id = args.get('resource_id')
        self.verify_ckan_ssl = args.get('verify_ckan_ssl')
        self.ckan_server_url = args.get('ckan_server_url')
        self.timeout = args.get('timeout_sec')
        self.hxl_proxy_source_info_url = args.get('hxl_proxy_source_info_url')
        self.fs_check_info = args.get(KEY_FS_CHECK_INFO)
        # TODO remove testing api_key
        self.api_key = os.getenv('HDX_FSCHECK_API_KEY', os.getenv('HDX_GIS_API_KEY'))
        self.resource_update_api = '{}/{}'.format(args['ckan_api_base_url'], args['resource_update_action'])

        self.headers_for_ckan = {
            'User-Agent': args['hdx_user_agent'],
            'Authorization': self.api_key
        }

    def _resolve_state_and_message(self, fs_check_info_dict: dict) -> tuple[str, str]:
        if fs_check_info_dict.get("error"):
            return STATE_ERROR, fs_check_info_dict.get(
                "message", "File structure check failed"
            )
        return STATE_SUCCESS, "File structure check completed"

    def process(self) -> Optional[Response]:
        logger.info(
            "In fs_check for {}, {}".format(self.dataset_id, self.resource_id))
        fs_check_info_dict = {}
        try:
            # hxl_proxy_source_info_url = self.hxl_proxy_source_info_url
            # TODO uncomment next line and comment text line
            response = requests.get(self.hxl_proxy_source_info_url, allow_redirects=True, timeout=self.timeout)
            response.raise_for_status()
            # DEBUG - for local env
            # response = requests.get(
            #     'https://data.humdata.org/hxlproxy/api/source-info?url=https://data.humdata.org/dataset/6c4c69cf-8ca0-4bfc-8c46-73cdb18812d5/resource/cfe1321e-89ce-43f3-b067-6da4bbb3ca80/download/somalia-2022-post-gu-total-acute-malnutrition-burden-and-prevalence-for-aug-2022-to-jul-2023-by.xlsx',
            #     allow_redirects=True)
            logger.info("task done")
            fs_check_info_dict = json.loads(response.text)
            sheet_changes = self.process_fs_check_info_changes(fs_check_info_dict)
            state, message = self._resolve_state_and_message(fs_check_info_dict)
            self.push_information_back_to_ckan(
                fs_check_info_dict,
                sheet_changes,
                state=state,
                message=message,
            )
            return response
        except JSONDecodeError as ex:
            logger.warning(ex)
            self.push_information_back_to_ckan(
                fs_check_info_dict={"error": "JSONDecodeError", "details": str(ex)},
                sheet_changes=[],
                state=STATE_ERROR,
                message=str(ex),
            )
            return None
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as ex:
            logger.warning(f"HTTP request failed: {ex}")
            self.push_information_back_to_ckan(
                fs_check_info_dict={"error": ex.__class__.__name__, "details": str(ex)},
                sheet_changes=[],
                state=STATE_ERROR,
                message=str(ex),
            )
            return None
        except Exception as ex:
            logger.error(ex)
            self.push_information_back_to_ckan(
                fs_check_info_dict={"error": ex.__class__.__name__, "details": str(ex)},
                sheet_changes=[],
                state=STATE_ERROR,
                message=str(ex),
            )
            raise exceptions.HXLProxyException('hxl proxy error/exception')

    def push_information_back_to_ckan(self, fs_check_info_dict: dict, sheet_changes: list, state: str = STATE_SUCCESS, message: str = "File structure check completed"):

        if self.resource_update_api and self.api_key:
            try:
                # fs_check_info_json = json.dumps(fs_check_info_dict)
                if 'details' in fs_check_info_dict:
                    fs_check_info_dict['details'] = fs_check_info_dict['details'].replace("http://hxl:5000", "")
                data_json = json.dumps({
                    'id': self.resource_id,
                    'package_id': self.dataset_id,
                    'key': KEY_FS_CHECK_INFO,
                    'value': {
                        "state": state,
                        "message": message.replace("http://hxl:5000", ""),
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

    def process_fs_check_info_changes(self, data_dict: Dict) -> List[Dict[str, Any]]:
        sheet_changes = []
        if self.fs_check_info:
            _fs_check_info = json.loads(self.fs_check_info)
            success_item_list = [item for item in _fs_check_info if item.get('state') == STATE_SUCCESS]
            if success_item_list:
                last_success_item = success_item_list[-1]
                current_item = {
                    'state': STATE_SUCCESS,
                    'message': '',
                    'timestamp':'',
                    'hxl_proxy_response': data_dict
                }
                file_structure_event_list = dc.detect_file_structure_changes(current_item, last_success_item)
                for fse in file_structure_event_list:
                    sheet_changes.append({
                        'name':fse.sheet_id,
                        'event_type':fse.event_type,
                        'changed_fields':fse.changed_fields or '',
                    })

        return sheet_changes

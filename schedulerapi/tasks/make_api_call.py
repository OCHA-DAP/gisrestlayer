import logging
import json
import requests
import helpers.log_config as log_config

logger = logging.getLogger(__name__)


def schedule_api_task(args):
    ScheduledApiTask(args).call_api()


class ScheduledApiTask(log_config.LogConfigHelper):

    def __init__(self, args):
        super(ScheduledApiTask, self).__init__(args)

        self.task_args = args.get('task_args')
        self.verify_ckan_ssl = args.get('verify_ckan_ssl', True)
        self.api_key = args['ckan_api_key']
        self.api_url = '{}/{}'.format(args['ckan_api_base_url'], self.task_args.get('action'))

        self.basic_headers = {
            'User-Agent': args.get('hdx_user_agent')
        }

    def call_api(self):
        try:

            logger.warn('Executing remote API call: {}'.format(self.api_url))

            data_json = json.dumps(self.task_args.get('api_params'))

            if self.task_args.get('method') == 'post':
                headers = {'Authorization': self.api_key, 'content-type': 'application/json'}.update(self.basic_headers)
                r = requests.post(self.api_url, data=data_json,
                                  headers=headers,
                                  verify=self.verify_ckan_ssl)
            else:
                r = requests.get(self.api_url, params=self.task_args.get('api_params'),
                                 headers=self.basic_headers,
                                 verify=self.verify_ckan_ssl)

            logger.info('Response was: {}'.format(r.text))

            r.raise_for_status()

        except Exception as e:
            logger.error('Problem when trying to make api call:' + str(e))

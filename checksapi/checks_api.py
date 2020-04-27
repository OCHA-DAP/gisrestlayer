import logging
import flask

import ckanext.hdx_service_checker.checker as checker

g = flask.g
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

checks_api = Blueprint('checks_api', __name__)
logger.info('checks_api blueprint loaded')


@checks_api.route('/api/run-checks', methods=['GET'])
def run_checks():

    try:
        config_file_path = app.config['CHECKS_CONFIG_PATH']
        __add_config_for_spatial(app.config)
        result = checker.run_checks(config_file_path, app.config)
    except Exception as e:
        result = [
            {
                'name': 'Exception raised',
                'error_message': str(e),
                'result': 'Failed',
                'type': 'Exception Wrapper',
                'description': 'Remote checks could not be executed because an exception was raised',
                'subchecks': []
            }
        ]

    result_wrapper = {
        'result': result
    }
    return jsonify(result_wrapper)


def __add_config_for_spatial(config):
    search_str = '/tables'
    spatial_url = config.get('GIS_API_PATTERN', '')
    url_index = spatial_url.find(search_str)
    spatial_check_url = spatial_url[0:url_index + len(search_str)]
    config['CHECKS_SPATIAL_URL'] = spatial_check_url

import logging
import flask
import deleteapi.layers_cleaner as layers_cleaner


g = flask.g
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

delete_api = Blueprint('delete_api', __name__)
logger.info('delete_api blueprint loaded')

@delete_api.route('/api/delete-layers', methods=['GET'], defaults={'dry_run': 'true'})
@delete_api.route('/api/delete-layers/dry-run/<string:dry_run>', methods=['GET'])
def delete_layers(dry_run):
    try:
        db_params = {
            'db_host': app.config.get('DB_HOST', 'db'),
            'db_name': app.config.get('DB_NAME', 'gis'),
            'db_user': app.config.get('DB_USER', 'ckan'),
            'db_pass': app.config.get('DB_PASS', 'abc'),
            'db_port': app.config.get('DB_PORT', 5432),
            'table_name_prefix': app.config.get('TABLE_NAME_PREFIX', 'pre')
        }
        ckan_params = {
            'ckan_api_base_url': app.config.get('CKAN_API_BASE_URL'),
            'resource_id_list_action': app.config.get('RESOURCE_ID_LIST_ACTION'),
            'ckan_api_key': app.config.get('CKAN_API_KEY'),
            'verify_ckan_ssl': app.config.get('VERIFY_CKAN_SSL', True)
        }

        dry_run_bool = False if dry_run == 'false' else True
        cleaner = layers_cleaner.LayersCleaner(db_params, ckan_params, app.config.get('HDX_USER_AGENT'), dry_run_bool)
    except Exception, e:
        logger.error('There was a problem initializing the cleaning process: {}'.format(str(e)))
        data_dict = {}
        data_dict['state'] = 'failure'
        data_dict['message'] = str(e)
        data_dict['error_class'] = type(e).__name__
        data_dict['type'] = 'cleaner-init-problem'
        return jsonify(data_dict)

    result = cleaner.process()
    json_result = jsonify(result)
    logger.debug('Result is: {}'.format(str(result)))
    return json_result


import logging
import flask
import deleteapi.layers_cleaner as layers_cleaner
import helpers.db_helper as db_helper
from helpers.helpers import generate_table_name, get_db_params_from_app_config

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
        db_host, db_name, db_pass, db_port, db_user, table_name_prefix = get_db_params_from_app_config(app.config)
        db_params = {
            'db_host': db_host,
            'db_name': db_name,
            'db_user': db_user,
            'db_pass': db_pass,
            'db_port': db_port,
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
    except Exception as e:
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


@delete_api.route('/api/delete-one-layer/<string:resource_id>', methods=['POST'])
def delete_layer(resource_id):
    status_code = 200
    result = {
        'state': 'started',
        'message': 'None',
        'error_type': 'None',
        'error_class': 'None'
    }
    try:
        db_host, db_name, db_pass, db_port, db_user, table_name_prefix = get_db_params_from_app_config(app.config)
        with db_helper.DbHelper(db_host, db_port, db_name, db_user, db_pass) as dbh:
            table_name = generate_table_name(table_name_prefix, resource_id)
            sql = 'DROP TABLE "{}";'.format(table_name)
            logger.info('Deleting layer {}'.format(table_name))
            dbh.exec_with_no_return(sql, None)

    except Exception as e:
        status_code = 500
        result['state'] = 'failure'
        result['message'] = str(e)
        result['error_class'] = type(e).__name__
        try:
            result['type'] = e.type
        except AttributeError:
            result['type'] = 'unknown'

    return jsonify(result), status_code

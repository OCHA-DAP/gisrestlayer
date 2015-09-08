import logging
import flask


import importapi.exceptions.exceptions as exceptions
import importapi.tasks.create_preview as create_preview_task


g = flask.g
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

import_api = Blueprint('import_api', __name__)
logger.info('import_api blueprint loaded')

# redis_connection = Redis(host='redis', db=1)
# redis_connection = Redis(host=app.config.get('REDIS_HOST', 'redis'), db=app.config.get('REDIS_DB', 1),
#                          port=app.config.get('REDIS_PORT', 6379))

# q = Queue("geo_q", connection=redis_connection)

@import_api.route('/api/add-layer/dataset/<string:dataset_id>/resource/<string:resource_id>', methods=['GET'])
def add_layer(dataset_id, resource_id):
    from gis_rest_layer import q
    data_dict = {
        'state': 'processing',
        'message': 'The processing of the geo-preview has started',
        'layer_id': 'None',
        'error_type': 'None',
        'error_class': 'None'
    }

    try:
        download_url = _get_download_url(request)
        task_arguments = {
            'dataset_id': dataset_id,
            'resource_id': resource_id,
            'download_url':  download_url,
            'url_type': _get_url_type(request),
            'max_file_size_mb': app.config.get('MAX_FILE_SIZE_MB',1) * 1024 * 1024,
            'timeout_sec': app.config.get('TIMEOUT_SEC', 1),
            # 'worker_timeout_sec': app.config.get('RQ_WORKER_TIMEOUT', 180),
            'ckan_api_key': app.config.get('CKAN_API_KEY'),
            'resource_update_api': app.config.get('RESOURCE_UPDATE_API'),
            'gis_api_pattern': app.config.get('GIS_API_PATTERN'),
            'table_name_prefix': app.config.get('TABLE_NAME_PREFIX', 'pre'),

            'db_host': app.config.get('DB_HOST', 'db'),
            'db_name': app.config.get('DB_NAME', 'gis'),
            'db_user': app.config.get('DB_USER', 'ckan'),
            'db_pass': app.config.get('DB_PASS', 'abc'),
            'db_port': app.config.get('DB_PORT', 5432),
            'tmp_download_directory': app.config.get('TMP_DOWNLOAD_DIRECTORY', '/tmp'),

            'ckan_server_url': app.config.get('CKAN_SERVER_URL', 'data.hdx.rwlabs.org'),
            'verify_ckan_ssl': app.config.get('VERIFY_CKAN_SSL', True),

            'logging_config': app.config.get('LOGGING_CONF_FILE')

        }

        q.enqueue_call(func=create_preview_task.create_preview_task, args=[task_arguments],
                       timeout=app.config.get('RQ_WORKER_TIMEOUT', 180))
        # For debugging purposes, comment line above and uncomment line below.
        # That way no rq tasks will be created.
        #  create_preview_task.create_preview_task(task_arguments)

        logger.debug("Started create_preview_task for {}, {}, {}".format(dataset_id, resource_id, download_url))

    except Exception, e:
        data_dict['state'] = 'failure'
        data_dict['message'] = str(e)
        data_dict['error_class'] = type(e).__name__
        data_dict['error_type'] = 'transformation-init-problem'

    logger.debug('Returning immediately: {}'.format(str(data_dict)))
    result = jsonify(data_dict)

    return result


def _get_download_url(request):
    try:
        return request.args['resource_download_url']
    except Exception, e:
        raise exceptions.MissingUrlException("Url missing or has a problem", [e])

def _get_url_type(request):
    return request.args.get('url_type', 'api')


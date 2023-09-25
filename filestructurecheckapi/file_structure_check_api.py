import logging
import flask
import filestructurecheckapi.tasks.file_structure_check as fs_check

g = flask.g
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

fs_check_api = Blueprint('file_structure_check_api', __name__)
fs_check_api_dict = {}
logger.info('file_structure_check_api blueprint loaded')


@fs_check_api.route('/api/file-structure-check/dataset/<string:dataset_id>/resource/<string:resource_id>',
                    methods=['POST'])
def file_structure_check(dataset_id, resource_id):
    call_arguments = request.get_json()
    fs_check_q = fs_check_api_dict.get('fs_check_q')
    fs_check_args = {
        'dataset_id': dataset_id,
        'resource_id': resource_id,
        # 'url_type': request.args.get('url_type'),
        # 'url': request.args.get('url'),
        'hxl_proxy_source_info_url': call_arguments.get('hxl_proxy_source_info_url'),
        'ckan_api_base_url': app.config.get('CKAN_API_BASE_URL'),
        'resource_update_action': app.config.get('HDX_FS_CHECK_RESOURCE_REVISE'),
        'verify_ckan_ssl': app.config.get('VERIFY_CKAN_SSL', True),
        'hdx_user_agent': app.config.get('HDX_USER_AGENT'),
        'fs_check_info': call_arguments.get('fs_check_info')
    }

    fs_check_q.enqueue_call(func=fs_check.fs_check_task, args=[fs_check_args],
                            timeout=app.config.get('RQ_WORKER_TIMEOUT', 180))
    # For debugging purposes comment the line above and uncomment the line below. This will avoid the redis queue
    # fs_check.fs_check_task(fs_check_args)

    result = {'success': True}
    return jsonify(result)

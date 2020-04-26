import logging
import flask

from datetime import datetime, timedelta


import schedulerapi.tasks.make_api_call as make_api_call

g = flask.g
request = flask.request
Blueprint = flask.Blueprint
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

scheduler_api = Blueprint('scheduler_api', __name__)
scheduler_api_dict = {}
logger.info('scheduler_api blueprint loaded')


@scheduler_api.route('/api/scheduler/add_job', methods=['POST'])
def add_job():
    '''
    Expects something like below in POST body

    .. code-block:: json

      {
        "action": "ckan_action",
        "method": "post",
        "sch_minutes": 1,
        "sch_hours": 1,
        "sch_days": 1,
        "api_params": {
            "id": "simple-analytics-test-5"
        }
      }

    :return: json of the form: `{'success': False, 'message': 'error message'}`
    :rtype: str
    '''
    scheduler = scheduler_api_dict.get('scheduler')

    try:
        call_arguments = request.get_json()

        timedelta_args = {}

        def set_timedelta_arg(name):
            call_arguments_name = 'sch_{}'.format(name)
            if call_arguments_name in call_arguments:
                timedelta_args[name] = call_arguments[call_arguments_name]

        set_timedelta_arg('minutes')
        set_timedelta_arg('hours')
        set_timedelta_arg('days')

        delta = timedelta(**timedelta_args)

        args = {
            'logging_config': app.config.get('LOGGING_CONF_FILE'),
            'timedelta': delta,
            'verify_ckan_ssl': app.config.get('VERIFY_CKAN_SSL', True),
            'ckan_api_key': app.config.get('CKAN_API_KEY'),
            'ckan_api_base_url': app.config.get('CKAN_API_BASE_URL'),
            'task_args': call_arguments,
            'hdx_user_agent': app.config.get('HDX_USER_AGENT')
        }

        scheduler.enqueue_in(delta, make_api_call.schedule_api_task, args=args,
                           timeout=app.config.get('RQ_WORKER_TIMEOUT', 180))

        # make_api_call.schedule_api_task(args)

        result = {'success': True}
    except Exception as e:
        error_message = 'Could not schedule job: {}'.format(str(e))
        logger.error(error_message)
        result = {'success': False, 'message': error_message}
    return jsonify(result)


@scheduler_api.route('/api/scheduler/list_jobs', methods=['GET'])
def list_jobs():
    scheduler = scheduler_api_dict.get('scheduler')

    job_list = scheduler.get_jobs()
    result = {
        'jobs': [{
                     'id': job.get_id(),
                     'created_at': str(job.created_at),
                     'description': job.description
                 } for job in job_list],
        'success': True
    }
    return jsonify(result)
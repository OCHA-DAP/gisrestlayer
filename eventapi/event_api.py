import logging

import flask

from eventapi.tasks.detect_changes import detect_changes

g = flask.g
request = flask.request
Blueprint = flask.Blueprint
make_response = flask.make_response
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

event_api = Blueprint('event_api', __name__)
logger.info('event_api blueprint loaded')

event_api_dict = {}


@event_api.route('/api/create-change-events', methods=['POST'])
def create_change_events():
    result = {
        'state': 'success'
    }
    try:
        task_arguments = request.get_json()

        event_q = event_api_dict.get('event_q')

        event_q.enqueue_call(func=detect_changes, args=[task_arguments],
                                 timeout=app.config.get('RQ_WORKER_TIMEOUT', 180))
        # For debugging purposes comment the line above and uncomment the line below. This will avoid the redis queue
        # detect_changes(task_arguments)

    except Exception as e:
        result['state'] = 'failure'
        result['message'] = str(e)
        logger.error('There was a problem processing the request: {}'.format(str(e)))

    return jsonify(result)

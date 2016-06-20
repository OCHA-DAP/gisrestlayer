import logging
import flask

import analyticsapi.tasks.send_event as send_event

g = flask.g
request = flask.request
Blueprint = flask.Blueprint
jsonify = flask.jsonify

logger = logging.getLogger(__name__)

app = flask.current_app

analytics_api = Blueprint('analytics_api', __name__)
logger.info('analytics_api blueprint loaded')


@analytics_api.route('/api/send-analytics', methods=['POST'])
def add_layer():
    from gis_rest_layer import analytics_q

    event_arguments = request.get_json()

    analytics_q.enqueue_call(func=send_event.send_event_task, args=[event_arguments],
                       timeout=app.config.get('RQ_WORKER_TIMEOUT', 180))
    # For debugging purposes comment the line above and uncomment the line below. This will avoid the redis queue
    # send_event.send_event_task(event_arguments)

    result = {'success': True}
    return jsonify(result)
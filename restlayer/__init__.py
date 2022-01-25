import logging
import logging.config

import flask
import rq_dashboard
import rq_scheduler
import werkzeug.exceptions as wexceptions
from redis import Redis
from rq import Queue

from restlayer.version import VERSION

g = flask.g
Flask = flask.Flask
make_response = flask.make_response
jsonify = flask.jsonify


def create_app():

    app = Flask(__name__)

    app.config.from_object('config.app_config.Config')
    app.config.from_envvar('GIS_REST_LAYER_CONF')
    app.config['DEBUG'] = False

    logging.config.fileConfig(app.config.get('LOGGING_CONF_FILE'))
    logger = logging.getLogger(__name__)
    logger.info('Starting Application GISRestLayer')

    redis_connection = Redis(host=app.config.get('REDIS_HOST', 'redis'), db=app.config.get('REDIS_DB', 1),
                             port=app.config.get('REDIS_PORT', 6379))

    geo_q = Queue("geo_q", connection=redis_connection)
    analytics_q = Queue("analytics_q", connection=redis_connection)
    default_scheduler_q = Queue("default_scheduler_q", connection=redis_connection)

    scheduler = rq_scheduler.Scheduler(queue_name='default_scheduler_q', connection=redis_connection)


    # for code in wexceptions.default_exceptions.iterkeys():
    #     app.error_handler_spec[None][code] = make_json_error

    import deleteapi.delete_api as delete_api
    import importapi.import_api as import_api
    import checksapi.checks_api as checks_api
    import analyticsapi.analytics_api as analytics_api
    import schedulerapi.scheduler_api as scheduler_api

    app.register_blueprint(import_api.import_api)
    app.register_blueprint(delete_api.delete_api)
    app.register_blueprint(checks_api.checks_api)
    app.register_blueprint(analytics_api.analytics_api)
    app.register_blueprint(scheduler_api.scheduler_api)

    import_api.import_api_dict['geo_q'] = geo_q
    analytics_api.analytics_api_dict['analytics_q'] = analytics_q
    scheduler_api.scheduler_api_dict['scheduler'] = scheduler

    # rq_dashboard.RQDashboard(app, url_prefix='/monitor')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix=app.config.get('MONITOR_URL', '/monitor'))

    @app.route('/version', methods=['GET'])
    @app.route('/about', methods=['GET'])
    def about():
        return flask.jsonify({"version": VERSION})

    @app.errorhandler(Exception)
    def make_json_error(ex):
        logger.error(str(ex))
        resp = {
            'message': str(ex),
            'state': 'failure',
            'error_class': type(ex).__name__,
            'error_type': 'transformation-init-problem'
        }
        response = jsonify(resp)
        response.status_code = (ex.code
                                if isinstance(ex, wexceptions.HTTPException)
                                else 500)
        return response

    return app

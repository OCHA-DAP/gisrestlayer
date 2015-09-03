import flask

import logging
import logging.config

import rq_dashboard

from redis import Redis
from rq import Queue

g = flask.g
Flask = flask.Flask
make_response = flask.make_response
jsonify = flask.jsonify

app = Flask(__name__)


app.config.from_object('config.app_config.Config')
app.config.from_envvar('GIS_REST_LAYER_CONF')
app.config['DEBUG'] = False

logging.config.fileConfig(app.config.get('LOGGING_CONF_FILE'))
logger = logging.getLogger(__name__)
logger.info('Starting Application GISRestLayer')

redis_connection = Redis(host=app.config.get('REDIS_HOST', 'redis'), db=app.config.get('REDIS_DB', 1),
                         port=app.config.get('REDIS_PORT', 6379))
q = Queue("geo_q", connection=redis_connection)

@app.errorhandler(404)
def page_not_found(error):
    data_dict = {
        'success': 'false',
        'message': 'Page Not Found',
        'error_type': 'page-not-found',
        'error_class': 'none'
    }


import deleteapi.delete_api as delete_api
import importapi.import_api as import_api
app.register_blueprint(import_api.import_api)
app.register_blueprint(delete_api.delete_api)

rq_dashboard.RQDashboard(app, url_prefix='/monitor')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.get('APP_PORT', '5000'), processes=1 )

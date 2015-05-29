import api.import_api as import_api
import flask

import logging
import logging.config

Flask = flask.Flask
make_response = flask.make_response
jsonify = flask.jsonify

app = Flask(__name__)
app.config.from_object('config.app_config.Config')
app.config.from_envvar('GIS_REST_LAYER_CONF')



logging.config.fileConfig(app.config.get('LOGGING_CONF_FILE'))
logger = logging.getLogger(__name__)
logger.info('Starting Application GISRestLayer')


@app.errorhandler(404)
def page_not_found(error):
    data_dict = {
        'success': 'false',
        'message': 'Page Not Found',
        'error_type': 'page-not-found',
        'error_class': 'none'
    }

app.register_blueprint(import_api.import_api)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=app.config.get('APP_PORT', '5000'))



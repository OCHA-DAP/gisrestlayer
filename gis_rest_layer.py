import api.import_api as import_api
from flask import Flask

import logging
import logging.config


app = Flask(__name__)
app.config.from_object('config.app_config.Config')
app.config.from_envvar('GIS_REST_LAYER_CONF')

logging.config.fileConfig(app.config.get('LOGGING_CONF_FILE'))

app.register_blueprint(import_api.import_api)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

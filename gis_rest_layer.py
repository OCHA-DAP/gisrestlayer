import config.app_config as app_config
import api.import_api as import_api
from flask import Flask



app = Flask(__name__)
app.config.from_object('config.app_config.Config')
app.config.from_envvar('GIS_REST_LAYER_CONF')


app.register_blueprint(import_api.import_api)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

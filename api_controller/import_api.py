import flask

Flask = flask.Flask
jsonify = flask.jsonify
request = flask.request
Blueprint = flask.Blueprint

app = flask.current_app

import_api = Blueprint('import_api', __name__)



@import_api.route('/api/add-layer/<string:dataset_id>/<string:resource_id>', methods=['GET'])
def add_layer(dataset_id, resource_id):
    download_url = request.args.get('resource_download_url', '')
    data_dict = {
        'success': 'true',
        'message': 'Import successful',
        'error_type': 'Timeout',
    }
    print 'aaa ' + str(app.config.get('MAX_FILE_SIZE_MB',''))
    return jsonify(data_dict)
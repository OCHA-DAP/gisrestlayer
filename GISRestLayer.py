from flask import Flask, jsonify

import json

app = Flask(__name__)


@app.route('/api/add-layer/<string:dataset_id>/<string:resource_id>', methods=['GET'])
def add_layer(dataset_id, resource_id):
    data_dict = {
        'dataset': dataset_id,
        'resource': resource_id
    }
    return jsonify(data_dict)




if __name__ == '__main__':
    app.run()

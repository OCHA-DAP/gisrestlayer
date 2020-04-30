import pytest
from flask import url_for


def test_add_layer(client, context_app, empty_geo_q):
    q = empty_geo_q
    assert len(q) == 0
    url = url_for('import_api.add_layer', dataset_id='some_dataset', resource_id='some_resource',
                  url_type='api', resource_download_url="https://example.com/test.csv")
    client.get(url)
    assert len(q) == 1

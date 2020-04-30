import pytest
from flask import url_for


def test_rq_monitor_endpoint_is_up(client, context_app):
    response = client.get(url_for('rq_dashboard.overview'))
    assert response.status_code == 200
    assert 'Workers' in response.data.decode('utf-8')


def test_checks_api_endpoint_is_up(client, context_app):
    response = client.get(url_for('checks_api.run_checks'))
    assert response.status_code == 200
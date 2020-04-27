import pytest
from restlayer import create_app


@pytest.fixture(scope='module')
def app():
    app = create_app()
    return app


@pytest.fixture(scope='module')
def context_app(app):
    print ('zzzzzz')
    with app.test_request_context():
        print('xxxxx')
        yield

    # def run_at_the_end():
    #     print('BBB')
    #     opened_app.close()
    #
    # request.addfinalizer(run_at_the_end)


@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def empty_geo_q(app):
    import importapi.import_api as import_api
    q = import_api.import_api_dict.get('geo_q')
    q.empty()
    return q



class Config(object):
    DEBUG = False
    APP_PORT = 5000
    MAX_FILE_SIZE_MB = 300
    TIMEOUT_SEC = 120

    DB_NAME = 'gis'
    DB_USER = 'postgres'
    DB_HOST = 'db'
    DB_PORT = 5432

    TMP_DOWNLOAD_DIRECTORY = '/tmp'

    GIS_API_PATTERN = 'http://localhost/services/tables/{table_name}'

    # Needed to push the results back to CKAN
    RESOURCE_UPDATE_API = 'http://172.17.42.1:5000/api/action/hdx_resource_update_metadata'

    # No worries, this is a dummy api key
    CKAN_API_KEY = 'e2a174b1-4d1c-42ac-afb3-28926b61a663'

    # URL or hostname of the redis server
    REDIS_HOST = 'redis'

    LOGGING_CONF_FILE = 'logging.conf'

    # REDIS SPECIFIC CONFIGURATION
    #: If set the REDIS_URL takes precedence over REDIS_HOST, REDIS_PORT, etc
    REDIS_URL = None

    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 1

    RQ_POLL_INTERVAL = 2500  #: Web interface poll period for updates in ms

    # How long can a worker work on a task
    RQ_WORKER_TIMEOUT = 300

    DEBUG = False

    CKAN_SERVER_URL = 'data.hdx.rwlabs.org'

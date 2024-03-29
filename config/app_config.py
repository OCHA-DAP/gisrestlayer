

class Config(object):
    DEBUG = False
    APP_PORT = 5000
    MAX_FILE_SIZE_MB = 300
    DOWNLOAD_CHUNK_SIZE_MB = 5
    TIMEOUT_SEC = 120

    DB_NAME = 'gis'
    DB_USER = 'postgres'
    DB_PASS = 'abc'
    DB_HOST = 'db'
    DB_PORT = 5432

    TMP_DOWNLOAD_DIRECTORY = '/tmp'

    GIS_API_PATTERN = 'http://localhost/services/tables/{table_name}'

    # Base url need to build calls to CKAN API
    CKAN_API_BASE_URL = 'http://172.17.42.1:5000/api/action'

    # Needed to push the results back to CKAN
    RESOURCE_UPDATE_ACTION = 'hdx_resource_update_metadata'

    HDX_FS_CHECK_RESOURCE_REVISE = 'hdx_fs_check_resource_revise'

    # Needed for finding all existing resources
    RESOURCE_ID_LIST_ACTION = 'hdx_resource_id_list'

    # No worries, this is a dummy api key
    CKAN_API_KEY = 'e2a174b1-4d1c-42ac-afb3-28926b61a663'

    LOGGING_CONF_FILE = 'logging.conf'

    # REDIS SPECIFIC CONFIGURATION
    #: If set the REDIS_URL takes precedence over REDIS_HOST, REDIS_PORT, etc
    # REDIS_URL = None

    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    # REDIS_PASSWORD = None
    REDIS_DB = 1

    RQ_DASHBOARD_POLL_INTERVAL = 2500  #: Web interface poll period for updates in ms

    # How long can a worker work on a task
    RQ_WORKER_TIMEOUT = 300

    CKAN_SERVER_URL = 'replace.with.url.of.ckan.server'
    VERIFY_CKAN_SSL = True

    # Path to json config file for checks
    CHECKS_CONFIG_PATH = '/srv/gislayer/config/config.json'

    # User Agent that will be used when making calls
    HDX_USER_AGENT = 'GISLAYER'

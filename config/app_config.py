

class Config(object):
    DEBUG = False
    MAX_FILE_SIZE_MB = 100
    TIMEOUT_SEC = 120

    DB_NAME = 'gis'
    DB_USER = 'postgres'
    DB_HOST = 'db'

    GIS_API_PATTERN = 'http://localhost/services/tables/{table_name}'

    LOGGING_CONF_FILE = 'logging.conf'

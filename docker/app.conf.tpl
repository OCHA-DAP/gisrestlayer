
DEBUG = False
APP_PORT = 5000
MAX_FILE_SIZE_MB = 300
TIMEOUT_SEC = 120
LOGGING_CONF_FILE = 'logging.conf'

REDIS_HOST = '${HDX_REDIS_HOST}'
REDIS_PORT = ${HDX_REDIS_PORT}
REDIS_DB = ${HDX_REDIS_GISDB}

VERIFY_CKAN_SSL=False

TMP_DOWNLOAD_DIRECTORY = '${HDX_GIS_TMP}'

# gisapi url
# GIS_API_PATTERN = 'http://${HDX_PREFIX}data.${HDX_DOMAIN}/gis/services/tables/{table_name}'
GIS_API_PATTERN = 'http://gisapi/services/tables/{table_name}'

# gispreviewbot's key
CKAN_API_KEY = '${HDX_GIS_API_KEY}'
# point to our ckan
CKAN_SERVER_URL = '${HDX_DOMAIN}'

# Base url need to build calls to CKAN API
# CKAN_API_BASE_URL = 'http://${HDX_PREFIX}data.${HDX_DOMAIN}/api/action'
CKAN_API_BASE_URL = 'http://ckan:5000/api/action'

CHECKS_CONFIG_PATH = '/srv/gislayer/config/config.json'

HDX_USER_AGENT = '${HDX_USER_AGENT}'

DB_HOST = '${DB_HOST}'
DB_PORT = '${DB_PORT}'
DB_NAME = '${DB_NAME}'
DB_USER = '${DB_USER}'
DB_PASS = '${DB_PASS}'

DEBUG = False
APP_PORT = 5000
MAX_FILE_SIZE_MB = 300
TIMEOUT_SEC = 120
LOGGING_CONF_FILE = 'logging.conf'

DB_NAME = '${HDX_GISDB_DB}'  
DB_USER = '${HDX_GISDB_USER}'
DB_PASS = '${HDX_GISDB_PASS}'
DB_HOST = 'gisdb'
DB_PORT = '5432'

REDIS_HOST = 'gisredis'
REDIS_PORT = 6379

VERIFY_CKAN_SSL=False

TMP_DOWNLOAD_DIRECTORY = '${HDX_GIS_TMP}'

# gisapi url
GIS_API_PATTERN = 'http://${HDX_PREFIX}data.${HDX_DOMAIN}/gis/services/tables/{table_name}'
# gispreviewbot's key
CKAN_API_KEY = '${HDX_GIS_API_KEY}'
# point to our ckan
CKAN_SERVER_URL = '${HDX_PREFIX}data.${HDX_DOMAIN}'

CKAN_API_BASE_URL = 'http://${HDX_PREFIX}data.${HDX_DOMAIN}/api/action'

CHECKS_CONFIG_PATH = '/srv/gislayer/config/config.json'

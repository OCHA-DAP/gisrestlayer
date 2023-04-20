def get_db_params_from_app_config(config):
    db_host = config.get('DB_HOST', 'db')
    db_name = config.get('DB_NAME', 'gis')
    db_user = config.get('DB_USER', 'ckan')
    db_pass = config.get('DB_PASS', 'abc')
    db_port = config.get('DB_PORT', 5432)
    table_name_prefix = config.get('TABLE_NAME_PREFIX', 'pre')
    return db_host, db_name, db_pass, db_port, db_user, table_name_prefix


def generate_table_name(table_name_prefix, resource_id):
    main_part = ''.join(i if i.isalnum() else '_' for i in resource_id)
    layer_id = "{}_{}".format(table_name_prefix, main_part)
    return layer_id
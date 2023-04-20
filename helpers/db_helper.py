import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


class DbHelper(object):

    def __init__(self, db_host, db_port, db_name, db_user, db_pass):
        self.con = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass)
        logger.debug('Pg connection initialized')

    def __enter__(self):
        return  self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.close()
        else:
            self.close(commit=True)

    def fetch_one_item(self, query, params):
        result = None
        with self.con.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
        return result[0]

    def fetch_list(self, query, params):
        result = None
        with self.con.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = [row[0] for row in rows]
        return result

    def fetch_dictionary(self, query, params):
        result = None
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = [{key: value for key, value in row.items()} for row in rows]
        return result

    def exec_with_no_return(self, query, params):
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, params)

    def exec_return_affected_rows(self, query, params):
        result = 0
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, params)
            result = cursor.rowcount

        return result

    def close(self, commit=False):
        if commit:
            self.con.commit()
        self.con.close()
        logger.debug('Pg connection closed')

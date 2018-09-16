import mysql.connector
from mysql.connector import Error


def keep_conn_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            self = args[0]
            database = self._params['db']['db_from']
            print('decorator db params:', database)
            billing_db = mysql.connector.connect(**database)
            def sender(is_dictionary=False, query=False, conditions=False, is_and=True, many=True):
                cursor = billing_db.cursor(dictionary=is_dictionary)
                if conditions:
                    c_list = []
                    for condition in conditions:
                        c_list.append(condition)
                    conditions = ' %s ' % (' and ' if is_and else ' or ').join(conditions)
                    query = '%s where %s' % (query, conditions)
                cursor.execute(query)
                if many:
                    query_result = cursor.fetchall()
                else:
                    query_result = cursor.fetchone()
                return query_result

            result = func(*args, sender=sender, **kwargs)
            return result
        except Error as e:
            print(e)
        finally:
            billing_db.close()

    return wrapper

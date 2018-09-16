import os
import re
import sys
import time
import mysql.connector
from mysql.connector import Error
from .config import *
from .decorators import keep_conn_decorator


class MessageSender:
    """ Main class """

    class _Node:
        """ Additional class for collecting data """
        __slots__ = ('message', 'number', 'login', 'dept')

        def __init__(self, number=None, message=None, login=None, **params):
            self.number = self._normalize_number(number)
            self.login = login
            self.dept = params['dept'] if 'dept' in params.keys() else None
            self.message = self._normalize_message_template(message)

        @staticmethod
        def _normalize_number(number):
            number = '38%s' % re.sub('^38', '', re.sub('[^\d]', '', number))
            return number

        def _normalize_message_template(self, message):
            key_mapper = {'<l>': self.login, '<n>': self.number, '<d>': self.dept}
            keys = re.findall('<\w>', message)
            message = re.sub('<\w>', '%s', message)
            if len(keys) != 0:
                keys = [key_mapper[key] for key in keys]
                message = message % (*keys,)
            return message

        def __str__(self):
            return '_Node <login: %s, number:%s, dept:%s>' % (self.login, self.number, self.dept)

    def __init__(self, message=False, turbosend=False, login=False, numbers=False, address=False,
                 debug=False, **params):
        print('****TESTTESTTEST*****')
        self._params = params
        print('CORE_PARAMS', self._params)
        self._debug = debug
        self._message = message if message else BASE_PAYMENTS_MESSAGE
        self._numbers = self._clean_number(numbers) if numbers else None
        self._address = self._clean_address(address) if address else None
        if not numbers and not address and not login:
            self._login = self._clean_login('*')
        elif login:
            self._login = self._clean_login(login)
        else:
            self._login = None
        self._nodes = self._gather()

    def get_message(self):
        return self._message

    def get_length(self):
        return len(self._nodes)

    def send(self):
        nodes = self._nodes
        print('Ready to send. \n')
        database = self._params['db']['db_to']
        try:
            turbosms_db = mysql.connector.connect(**database)
            turbosms_cursor = turbosms_db.cursor()
            os.chdir('/tmp')
            test_file = open("%s.log" % (re.sub(r' ', '_', time.ctime())), "a")
            for node in nodes:
                print(node)
                if self._debug:
                    print(node.message)
                    print('INSERT INTO testinsert (number, message, sign, send_time) VALUES (%s, \'%s\', \'Tvintel\', NOW());' % (node.number, node.message))
                if len(node.number) == 12:
                    test_file.write(node.message + '\n')
                    turbosms_cursor.execute('INSERT INTO testinsert (number, message, sign, send_time) VALUES (\'%s\', \'%s\', \'Tvintel\', NOW());' % (node.number, node.message))
                    turbosms_db.commit()
                else:
                    test_file.write('Плохой номер: %s' % node.message)
                    nodes.pop(nodes.index(node))

        except Error as e:
            print(e)
        finally:
            turbosms_db.close()
            turbosms_cursor.close()
            return nodes

    # **** HELPERS ************************************************************

    def _get_info(self, is_dictionary=False, query=False, conditions=False, is_and=True):
        if conditions:
            conditions = ' %s ' % (' and ' if is_and else ' or ').join(conditions)
            query = '%s where %s' % (query, conditions)
        print(query)
        try:
            database = self._params['db']['db_from']
            billing_db = mysql.connector.connect(**database)
            billing_cursor = billing_db.cursor(dictionary=is_dictionary)
            billing_cursor.execute(query)
            result = billing_cursor.fetchall()
            # print('result', result)
        except Error as e:
            print(e)
        finally:
            billing_db.close()
            billing_cursor.close()
        return result

    @keep_conn_decorator
    def _gather(self, sender):
        info = []
        users_list = self._numbers or self._login or self._address

        def check_tag(dct):
            tags = sender(many=True,
                          query=get_tags,
                          conditions=['login=%s' % dct['login']])
            for tag in tags:
                if 1 in tag:
                    return available_tags_cost['1']
                if 2 in tag:
                    return available_tags_cost['2']
            return 0
        if users_list:
            for elem in users_list:
                if isinstance(elem, dict):
                    print(isinstance(elem, dict))
                    dept = -1
                    if 'depts' in self._params.keys() and self._params['depts'] is True:
                        available_tags_cost = {'1': 20, '2': 60, '0': 0}
                        dept = elem['cash'] - elem['Fee'] - check_tag(elem)
                    if elem['Down'] != 1 and elem['Passive'] != 1 and dept < 0:
                        if elem['TariffChange'] is not '':
                            elem['Fee'] = sender(many=False, query=get_tariff, conditions=['name=%s' % elem['users.tariff']])(0)
                        info.append(MessageSender._Node(message=self._message,
                                                        number=elem['phone'],
                                                        login=elem['login'],
                                                        dept=abs(round(dept))))
                else:
                    info.append(MessageSender._Node(message=self._message,
                                            number=elem))
        return info

    # *************************************************************************
    # ****** CLEANERS *********************************************************

    def _clean_address(self, address):
        conditions = []
        for address in address.split(', '):
            street = re.search('(?P<street>(\w)+(\s)?(\w)*)(\s)(?P<buildnum>[\w\d]+)$', address)
            if street:
                street = street.groupdict()
            else:
                return None
            conditions.append('streetname like \'%{}%\' and buildnum like \'{}\' and users.Down=0 and users.Passive=0'.format(re.sub(' ', '%', street['street']),
                                                                                         street['buildnum']))
        login_list = self._get_info(is_dictionary=False,
                                    is_and=False,
                                    conditions=conditions,
                                    query=get_streets)
        if login_list:
            conditions = ('users.login=%s' % login for login in login_list)
            data = self._get_info(is_dictionary=True,
                                  is_and=False,
                                  conditions=conditions,
                                  query=get_list)
            return data
        else:
            return None

    def _clean_number(self, numbers):
        numbers_list = []
        for n in numbers.split(', '):
            is_valid_number = re.search(
                '^(\+)?(\s)?(38)?(\()?0(\d{2})(\))?([-,\s])?(\d{3})([-,\s])?(\d{2})([-,\s])?(\d{2})$', n)
            if is_valid_number:
                numbers_list.append('38%s' % re.sub('[^\d]', '', re.sub('(^38)', '', is_valid_number.group())))
        phones = self._get_info(is_dictionary=True,
                                is_and=False,
                                query=get_phones)
        # print('GET_PHONES', phones)
        phones = ({'phone': re.sub('^38', '', re.sub('[^\d]', '', phone['phone'])), 'login': phone['login']} for phone in phones)
        phones = ['users.login=%s' % phone['login'] for phone in phones if '38%s' % phone['phone'] in numbers_list]
        print(phones)
        if phones:
            data = self._get_info(is_dictionary=True,
                                    is_and=False,
                                    conditions=phones,
                                    query=get_list)
        else:
            print('number', numbers_list)

            data = numbers_list
        return data

    def _clean_login(self, login):
        if not '*'in login:
            login_lst = login.split(', ')
            conditions = ['users.login=\'%s\'' % login for login in login_lst]
            is_and = False
        else:
            conditions = ['users.Down=0', 'users.Passive=0']
            is_and = True
        data = self._get_info(is_dictionary=True,
                              is_and=is_and,
                              conditions=conditions,
                              query=get_list)
        return data

    # **************************************
    # *******HANDLERS***********************


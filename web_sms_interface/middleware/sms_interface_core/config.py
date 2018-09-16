ban_alias = ['ah', 'kosh', 'hsh', 'virm', 'polar', 'mirn', 'rokos', 'minsk', 'rev', 'ol', 'verb', 'gr',
                 'dragom', 'mayor', 'kondr', 'dek', 'tash']

bad_tags = [4]

BASE_PAYMENTS_MESSAGE = "Popovnit Bud\\'laska vash rahunok #<l> na <d> grn, shob uniknuti vidkluchennia posluh u nastupnomu misyaci."

BASE_TO_MESSAGE = "Povidomliaemo Vas, z %s do %s godyni  budut\' provodutusia tehnichni robotu, mozhlivi problemi z dostupom v internet. Z povagoiu Tvintel."

get_corp_bans = "select login from corp_users"

get_payments_list = """select users.login, Fee, phones.phone,  users.tariff, users.cash, TariffChange, Down from users
                       inner join phones on phones.login=users.login
                       where Down=0 and Passive=0 and tariffs.Fee > 0 """


get_list = """select users.login, Fee, phones.phone, users.tariff, users.cash, TariffChange, Down, Passive from users
                       inner join phones on phones.login=users.login
                       inner join tariffs on tariffs.name=users.tariff
                       """

get_phones = "select phone, login from phones"

get_login = "select login from users"

#get_streets_from_streets = lambda lst, query: query % (' and '.join(lst))

get_streets = """select users.login from users
                                        inner join address on address.login=users.login
                                        inner join apt on address.aptid=apt.id
                                        inner join build on apt.buildid=build.id
                                        inner join street on build.streetid=street.id
                                        """

get_tags = """select tagid from tags"""

get_tariff = """ select Fee from tariffs
"""
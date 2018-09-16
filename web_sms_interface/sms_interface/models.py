from django.db import models
from django.contrib.auth.models import User, Permission
from django.shortcuts import reverse


class Message(models.Model):
    user = models.ManyToManyField(User, unique=False)
    number = models.CharField(max_length=12, null=False)
    message = models.CharField(max_length=145, null=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'date: %s, number: %s' % (self.date, self.number)


class DatabaseConfig(models.Model):
    config_name = models.CharField(max_length=50, default='some config name', verbose_name='Название конфига')
    name = models.CharField(max_length=50, default='some database', verbose_name='Имя БД')
    host = models.CharField(max_length=50, verbose_name='Хост БД')
    port = models.CharField(max_length=5, default='3306', verbose_name='Порт БД')
    db_table = models.CharField(max_length=20, default='', verbose_name='Таблица БД', blank=True)
    db_user = models.CharField(max_length=20, verbose_name='Пользователь БД')
    db_password = models.CharField(max_length=20, default='', blank=True, verbose_name='Пароль пользователя БД')
    db_charset = models.CharField(max_length=10, default='utf8', blank=True, verbose_name='Кодировка БД')
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')

    def get_fields_verbose(self):
        return (i._verbose_name for i in self._meta.fields if i._verbose_name != 'Удален')

    def get_fields(self):
        return (self.__dict__[i.name] for i in self._meta.fields if isinstance(i.name, str) and i._verbose_name != 'Удален')

    def __repr__(self):
        return self.config_name

    def __str__(self):
        return self.config_name


class MessageConfig(models.Model):
    name = models.CharField(max_length=50, default='default', verbose_name='Название конфигурации')
    db_from = models.ManyToManyField('DatabaseConfig', related_name='messageconfig_db_from', blank=True,
                                     verbose_name='База откуда')
    db_to = models.ManyToManyField('DatabaseConfig', related_name='messageconfig_db_to', blank=True, verbose_name='База куда')
    default_message = models.CharField(max_length=150,
                                       default="Popovnit Bud\\'laska vash rahunok #<l> na <d> grn, shob uniknuti vidkluchennia posluh u nastupnomu misyaci.", verbose_name='Стандартное сообщение')
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')

    def get_fields_verbose(self):
        field_names = []
        field_names.extend((i._verbose_name for i in self._meta.get_fields() if  i._verbose_name != 'Удален'))
        return field_names
    #
    # def get_fields(self):
    #     fields = DatabaseConfig.objects.get(id=self.id)
    #     return fields

    def __str__(self):
        return '%s' % (self.name)


class MyUser(User):

    class Meta:
        proxy = True

    def get_fields(self):
        return self._meta.get_fields(include_parents=True)

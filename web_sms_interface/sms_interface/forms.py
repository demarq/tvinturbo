from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import FieldError, NON_FIELD_ERRORS
from django.db import models
from .models import Message, DatabaseConfig, MessageConfig
from middleware.sms_interface_core import core, config
import re


def clean_input(message):
    message = re.sub('\'', '\\\'', message)
    return message


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

    def clean_username(self):
        username = clean_input(self.cleaned_data['username'])
        return username

    def clean_password(self):
        password = clean_input(self.cleaned_data['password'])
        return password

    def bad_login(self):
        self.add_error('username', 'Invalid login or password.')
        self.add_error('password', 'Invalid login or password.')


class SettingsForm(forms.ModelForm):
    widget = forms.TextInput(attrs={'class': 'form-control'})
    config_name = forms.CharField(error_messages={'required': 'Название конфига не может быть пустым'}, label='Название Конфига', widget=widget)
    name = forms.CharField(error_messages={'required': 'Имя БД не может быть пустым'}, label='Имя БД', widget=widget)
    host = forms.CharField(error_messages={'required': 'Хост БД не может быть пустым'}, label='Хост БД', widget=widget)
    db_table = forms.CharField(error_messages={'required': 'Таблица БД не может быть пустой'}, label='Таблица БД', widget=widget)
    port = forms.CharField(error_messages={'required': 'Порт БД не может быть пустым'}, label='Порт БД', widget=widget)
    db_user = forms.CharField(error_messages={'required': 'Пользователь БД не может быть пустым'}, label='Пользователь БД',
                              widget=widget
                              )
    db_password = forms.CharField(required=False, label='Пароль БД', widget=widget)
    db_charset = forms.CharField(label='Кодировка БД', empty_value='utf8', widget=widget
                                 )

    def clean_name(self):
        name = clean_input(self.cleaned_data['name'])
        return name

    def clean_host(self):
        host = clean_input(self.cleaned_data['host'])
        return host

    class Meta:
        model = DatabaseConfig
        exclude = ['is_deleted']


class MessageConfigForm(forms.ModelForm):
    widget = forms.TextInput(attrs={'class': 'form-control'})
    name = forms.CharField(error_messages={'required': 'Название конфига не может быть пустым'}, label='Название конфигурации', widget=widget)
    db_from = forms.ModelMultipleChoiceField(queryset=DatabaseConfig.objects.filter(is_deleted=False),
                                              label='Выбор биллинга',
                                              widget=forms.SelectMultiple(
                                                  attrs={'class': 'text-primary custom-select bg-dark',}))
    db_to = forms.ModelMultipleChoiceField(queryset=DatabaseConfig.objects.filter(is_deleted=False),
                                              label='Выбор Турбосмс',
                                              widget=forms.SelectMultiple(
                                                  attrs={'class': 'text-primary custom-select bg-dark',}))

    class Meta:
        model = MessageConfig
        exclude = ['is_deleted', 'default_message']


class DoSendForm(forms.Form):
    widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Необязательно'})
    settings = forms.ModelMultipleChoiceField(queryset=MessageConfig.objects.filter(is_deleted=False),
                                              label='Выбранные настройки',
                                              widget=forms.SelectMultiple(
                                                  attrs={'class': 'text-primary custom-select bg-dark',
                                                         'placeholder': 'Необязательно'}))

    message = forms.CharField(max_length=150, empty_value='', required=False, label='Отправляемое сообщение', widget=widget)
    login = forms.CharField(max_length=200, empty_value='', required=False, label='Логин', widget=widget)
    number = forms.CharField(max_length=200, empty_value='', required=False, label='Номер', widget=widget)
    address = forms.CharField(max_length=200, empty_value='', required=False, label='Адрес', widget=widget)
    calculate_depts = forms.BooleanField(required=False, label='Поcчитать долги?', widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    def clean_settings(self):
        settings = self.cleaned_data['settings']
        return settings.first()

    def clean_message(self):
        message = clean_input(self.cleaned_data['message'])
        return message

    def clean_login(self):
        login = clean_input(self.cleaned_data['login'])
        login = re.sub('[^\d]', '', login)
        return login

    def clean_address(self):
        address = clean_input(self.cleaned_data['address'])
        return address

    def confirm(self):
        settings = MessageConfig.objects.get(id=self.cleaned_data['settings'].id)
        bill = settings.db_from.first()
        tur = settings.db_to.first()
        params = {}
        params.update({'db_from': {'host': bill.host,
                                   'port': bill.port,
                                   'user': bill.db_user,
                                   'table': bill.db_table,
                                   'database': bill.name,
                                   'charset': bill.db_charset,
                                   'password': bill.db_password
                                   }})
        params.update({'db_to': {'host': tur.host,
                                 'port': tur.port,
                                 'user': tur.db_user,
                                 'database': tur.name,
                                 'table': tur.db_table,
                                 'charset': tur.db_charset,
                                 'password': tur.db_password
                                 }})

        return core.MessageSender(message=self.cleaned_data['message'],
                                  login=self.cleaned_data['login'],
                                  numbers=self.cleaned_data['number'],
                                  address=self.cleaned_data['address'],
                                  depts=self.cleaned_data['calculate_depts'],
                                  db=params,
                                  )


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput, label='Никнейм')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    email = forms.EmailField(label='Электронная почта')
    first_name = forms.CharField(widget=forms.TextInput, label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)

    def clean_username(self):
        un = self.cleaned_data['username']
        try:
            ifexist = User.objects.get(username=un)
            raise forms.ValidationError('Пользователь с таким никнеймом уже существует.')
        except models.ObjectDoesNotExist:
            pass

        return un

    def clean_password(self):
        password = self.cleaned_data['password']
        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            ifexist = User.objects.get(email=email)
            raise forms.ValidationError('Пользователь с таким электронным адресом уже существует.')
        except models.ObjectDoesNotExist:
            pass
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name

    def save(self):
        q = User.objects.create_user(**self.cleaned_data)
        return q


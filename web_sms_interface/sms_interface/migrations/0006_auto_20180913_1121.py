# Generated by Django 2.1.1 on 2018-09-13 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_interface', '0005_messageconfig_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databaseconfig',
            name='charset',
            field=models.CharField(blank=True, default='utf8', max_length=10),
        ),
        migrations.AlterField(
            model_name='databaseconfig',
            name='db user password',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]

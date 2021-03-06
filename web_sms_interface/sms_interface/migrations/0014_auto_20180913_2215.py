# Generated by Django 2.1.1 on 2018-09-13 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_interface', '0013_auto_20180913_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageconfig',
            name='db_from',
            field=models.ManyToManyField(related_name='messageconfig_db_from', to='sms_interface.DatabaseConfig'),
        ),
        migrations.AlterField(
            model_name='messageconfig',
            name='db_to',
            field=models.ManyToManyField(related_name='messageconfig_db_to', to='sms_interface.DatabaseConfig'),
        ),
    ]

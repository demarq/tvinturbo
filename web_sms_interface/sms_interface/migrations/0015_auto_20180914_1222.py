# Generated by Django 2.1.1 on 2018-09-14 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_interface', '0014_auto_20180913_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='databaseconfig',
            name='config_name',
            field=models.CharField(default='some config name', max_length=50),
        ),
        migrations.AlterField(
            model_name='messageconfig',
            name='db_from',
            field=models.ManyToManyField(blank=True, related_name='messageconfig_db_from', to='sms_interface.DatabaseConfig'),
        ),
        migrations.AlterField(
            model_name='messageconfig',
            name='db_to',
            field=models.ManyToManyField(blank=True, related_name='messageconfig_db_to', to='sms_interface.DatabaseConfig'),
        ),
    ]

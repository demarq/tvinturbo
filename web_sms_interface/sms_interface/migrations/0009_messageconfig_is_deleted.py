# Generated by Django 2.1.1 on 2018-09-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_interface', '0008_messageconfig_default_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='messageconfig',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
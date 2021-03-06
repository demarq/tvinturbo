# Generated by Django 2.1.1 on 2018-09-13 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sms_interface', '0009_messageconfig_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messageconfig',
            name='current_billing_db',
        ),
        migrations.AddField(
            model_name='messageconfig',
            name='current_billing_db',
            field=models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='cur_bil_db', to='sms_interface.DatabaseConfig'),
        ),
        migrations.RemoveField(
            model_name='messageconfig',
            name='current_turbosms_db',
        ),
        migrations.AddField(
            model_name='messageconfig',
            name='current_turbosms_db',
            field=models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='cur_tsms_db', to='sms_interface.DatabaseConfig'),
        ),
    ]

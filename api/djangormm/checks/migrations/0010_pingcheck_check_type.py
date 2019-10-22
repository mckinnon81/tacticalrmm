# Generated by Django 2.2.6 on 2019-10-13 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checks', '0009_auto_20191013_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingcheck',
            name='check_type',
            field=models.CharField(choices=[('diskspace', 'Disk Space Check'), ('ping', 'Ping Check'), ('cpuload', 'CPU Load Check'), ('memory', 'Memory Check')], default='ping', max_length=30),
        ),
    ]

# Generated by Django 2.2.3 on 2019-07-10 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checks', '0003_auto_20190710_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardcheck',
            name='cpuload',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

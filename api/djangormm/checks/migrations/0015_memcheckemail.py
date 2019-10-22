# Generated by Django 2.2.6 on 2019-10-13 22:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checks', '0014_auto_20191013_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemCheckEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent', models.DateTimeField(auto_now=True)),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checks.MemCheck')),
            ],
        ),
    ]

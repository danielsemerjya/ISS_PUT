# Generated by Django 3.1.5 on 2021-01-20 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pid_db',
            name='n',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='pid_db',
            name='t',
            field=models.FloatField(default=1),
        ),
    ]
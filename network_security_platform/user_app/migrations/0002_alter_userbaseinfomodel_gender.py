# Generated by Django 3.2.16 on 2024-10-02 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbaseinfomodel',
            name='gender',
            field=models.CharField(default='0', max_length=1, verbose_name='性别'),
        ),
    ]
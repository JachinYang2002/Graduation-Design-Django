# Generated by Django 3.2.16 on 2024-10-06 16:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CTF_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userwebquestionstatus',
            name='user_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_topic', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='userwebquestionstatus',
            name='web_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_topic', to='CTF_app.webchallenge', verbose_name='web题'),
        ),
        migrations.AlterUniqueTogether(
            name='userwebquestionstatus',
            unique_together={('user_tag', 'web_question')},
        ),
    ]
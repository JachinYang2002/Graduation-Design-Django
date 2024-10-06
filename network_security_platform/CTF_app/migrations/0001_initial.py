# Generated by Django 3.2.16 on 2024-10-06 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='题目名称')),
                ('description', models.TextField(verbose_name='题目描述')),
                ('points', models.IntegerField(default=30, verbose_name='奖励点')),
                ('exp', models.IntegerField(default=10, verbose_name='奖励经验')),
                ('flag', models.CharField(max_length=100, verbose_name='题目答案flag')),
            ],
            options={
                'verbose_name': 'Crypto题型的信息表',
                'verbose_name_plural': 'Crypto题型的信息表',
                'db_table': 't_CTF_crypto_info',
            },
        ),
        migrations.CreateModel(
            name='CTFQuestionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='题库类型')),
            ],
            options={
                'verbose_name': '题库类型表',
                'verbose_name_plural': '题库类型表',
                'db_table': 't_CTF_question_type',
            },
        ),
        migrations.CreateModel(
            name='MiscChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='题目名称')),
                ('description', models.TextField(verbose_name='题目描述')),
                ('points', models.IntegerField(default=30, verbose_name='奖励点')),
                ('exp', models.IntegerField(default=10, verbose_name='奖励经验')),
                ('flag', models.CharField(max_length=100, verbose_name='题目答案flag')),
            ],
            options={
                'verbose_name': 'Misc题型的信息表',
                'verbose_name_plural': 'Misc题型的信息表',
                'db_table': 't_CTF_misc_info',
            },
        ),
        migrations.CreateModel(
            name='PwnChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='题目名称')),
                ('description', models.TextField(verbose_name='题目描述')),
                ('points', models.IntegerField(default=30, verbose_name='奖励点')),
                ('exp', models.IntegerField(default=10, verbose_name='奖励经验')),
                ('flag', models.CharField(max_length=100, verbose_name='题目答案flag')),
            ],
            options={
                'verbose_name': 'Pwn题型的信息表',
                'verbose_name_plural': 'Pwn题型的信息表',
                'db_table': 't_CTF_pwn_info',
            },
        ),
        migrations.CreateModel(
            name='UserWebQuestionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_completed', models.BooleanField(default=False, verbose_name='是否完成')),
            ],
            options={
                'verbose_name': '用户Web题型解题状态表',
                'verbose_name_plural': '用户Web题型解题状态表',
                'db_table': 't_CTF_user_web_status',
            },
        ),
        migrations.CreateModel(
            name='WebChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='题目名称')),
                ('description', models.TextField(verbose_name='题目描述')),
                ('points', models.IntegerField(default=30, verbose_name='奖励点')),
                ('exp', models.IntegerField(default=10, verbose_name='奖励经验')),
                ('flag', models.CharField(max_length=100, verbose_name='题目答案flag')),
                ('question_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='web_list', to='CTF_app.ctfquestiontype', verbose_name='所属题目类型')),
            ],
            options={
                'verbose_name': 'Web题型的信息表',
                'verbose_name_plural': 'Web题型的信息表',
                'db_table': 't_CTF_web_info',
            },
        ),
        migrations.CreateModel(
            name='WebActiveChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_name', models.CharField(max_length=50, verbose_name='容器名称')),
                ('port', models.IntegerField(verbose_name='分配出的端口号')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_active_question', to='CTF_app.webchallenge', verbose_name='容器对应的镜像')),
            ],
            options={
                'verbose_name': 'Web题型分配出的端口号表',
                'verbose_name_plural': 'Web题型分配出的端口号表',
                'db_table': 't_CTF_web_active',
            },
        ),
    ]
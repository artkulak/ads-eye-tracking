# Generated by Django 3.1.3 on 2021-02-10 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_link', models.CharField(max_length=200)),
                ('video_name', models.CharField(max_length=200)),
            ],
        ),
    ]

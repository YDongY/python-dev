# Generated by Django 3.2.7 on 2021-10-18 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_alter_post_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('draft', '草稿'), ('published', '已发布')], default='draft', max_length=10),
        ),
    ]

# Generated by Django 3.1 on 2022-04-08 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0011_auto_20220121_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='category/thumbnail/'),
        ),
    ]

# Generated by Django 3.1 on 2022-05-26 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0014_auto_20220514_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='fee',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
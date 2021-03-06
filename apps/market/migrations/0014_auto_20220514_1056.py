# Generated by Django 3.1 on 2022-05-14 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0013_auto_20220428_0619'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='custom_address',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='unit_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='part_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

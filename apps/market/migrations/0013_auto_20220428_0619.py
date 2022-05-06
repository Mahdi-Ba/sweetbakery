# Generated by Django 3.1 on 2022-04-28 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_category_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name='product',
            name='extra_discount_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]

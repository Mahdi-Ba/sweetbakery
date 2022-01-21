# Generated by Django 3.1 on 2022-01-21 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_auto_20220121_1002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='state',
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.IntegerField(choices=[(0, 'Ordered Received'), (1, 'Ordered Processed'), (2, 'Order Ready to Deliver'), (3, 'Delivered')], default=0),
        ),
    ]

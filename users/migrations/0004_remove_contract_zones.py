# Generated by Django 2.1.3 on 2019-02-28 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_contract_zones'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='contract_zones',
        ),
    ]

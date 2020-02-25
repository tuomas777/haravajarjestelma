# Generated by Django 2.2.8 on 2020-02-22 23:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("areas", "0004_add_contract_zone_active_origin_id_contractor_name"),
    ]

    operations = [
        migrations.RemoveField(model_name="contractzone", name="contractor_user"),
        migrations.AddField(
            model_name="contractzone",
            name="contractor_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="contract_zones",
                to=settings.AUTH_USER_MODEL,
                verbose_name="contractor users",
            ),
        ),
    ]

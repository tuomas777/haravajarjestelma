# Generated by Django 2.1.3 on 2019-01-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("events", "0002_add_contract_zone")]

    operations = [
        migrations.AddField(
            model_name="event",
            name="equipment_information",
            field=models.TextField(
                blank=True, verbose_name="additional equipment information"
            ),
        )
    ]

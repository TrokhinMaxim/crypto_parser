# Generated by Django 5.0.4 on 2024-04-18 10:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("parser", "0002_rename_reciver_transactions_receiver"),
    ]

    operations = [
        migrations.AddField(
            model_name="transactions",
            name="crypto_name",
            field=models.CharField(default="Unknown", max_length=50),
        ),
    ]

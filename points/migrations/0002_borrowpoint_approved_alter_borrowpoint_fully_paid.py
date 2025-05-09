# Generated by Django 5.1.4 on 2025-04-27 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowpoint',
            name='approved',
            field=models.BooleanField(default=False, help_text='lender must approve to give loan to borrower'),
        ),
        migrations.AlterField(
            model_name='borrowpoint',
            name='fully_paid',
            field=models.BooleanField(default=False),
        ),
    ]

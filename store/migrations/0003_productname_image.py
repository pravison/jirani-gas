# Generated by Django 5.1.4 on 2025-04-28 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_productname_remove_product_product_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productname',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='gas'),
        ),
    ]

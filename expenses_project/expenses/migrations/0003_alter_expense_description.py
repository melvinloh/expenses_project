# Generated by Django 4.1.3 on 2022-12-05 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_alter_category_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]

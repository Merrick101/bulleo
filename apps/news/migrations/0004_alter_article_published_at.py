# Generated by Django 4.2.19 on 2025-03-06 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_newssource_alter_article_options_article_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='published_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

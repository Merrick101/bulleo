from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model("users", "Category")
    categories = [
        {"name": "World News", "slug": "world-news", "order": 1},
        {"name": "Politics", "slug": "politics", "order": 2},
        {"name": "Business", "slug": "business", "order": 3},
        {"name": "Technology", "slug": "technology", "order": 4},
        {"name": "Sports", "slug": "sports", "order": 5},
        {"name": "Entertainment", "slug": "entertainment", "order": 6},
    ]
    for cat in categories:
        Category.objects.get_or_create(name=cat["name"], defaults=cat)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_category_options_alter_profile_options_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_categories),
    ]

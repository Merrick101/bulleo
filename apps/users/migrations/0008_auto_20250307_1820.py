from django.db import migrations, models
import django.db.models.deletion

def forward(apps, schema_editor):
    # No changes are needed here, as the parent field already exists.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_comment_user'),
    ]

    operations = [
        # Remove the AddField operation that tries to add `parent` again
        # migrations.AddField(
        #     model_name='comment',
        #     name='parent',
        #     field=models.ForeignKey(
        #         null=True, blank=True, to='users.comment', on_delete=django.db.models.deletion.CASCADE, related_name='replies'
        #     ),
        # ),
    ]

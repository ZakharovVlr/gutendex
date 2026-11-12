from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_add_trgm_indexes'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='book',
            index=GinIndex(
                fields=['title'],
                name='book_title_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
        migrations.AddIndex(
            model_name='person',
            index=GinIndex(
                fields=['name'],
                name='person_name_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
    ]

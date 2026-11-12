from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_book_editors.py'),  
    ]

    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name='bookshelf',
            index=GinIndex(
                fields=['name'],
                name='bookshelf_name_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
        migrations.AddIndex(
            model_name='subject',
            index=GinIndex(
                fields=['name'],
                name='subject_name_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
    ]

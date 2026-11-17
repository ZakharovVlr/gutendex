from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_add_search_trgm_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='format',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='books_files/'),
        ),
        migrations.AlterField(
            model_name='format',
            name='mime_type',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='format',
            name='url',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]

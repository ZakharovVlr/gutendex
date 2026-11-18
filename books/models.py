from django.db import models


class Book(models.Model):
    authors = models.ManyToManyField('Person', blank=True)
    bookshelves = models.ManyToManyField('Bookshelf', blank=True)
    copyright = models.BooleanField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    editors = models.ManyToManyField("Person", related_name="books_edited", blank=True)
    gutenberg_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    languages = models.ManyToManyField('Language', blank=True)
    media_type = models.CharField(max_length=16, default='Text')
    subjects = models.ManyToManyField('Subject', blank=True)
    title = models.CharField(blank=True, max_length=1024, null=True)
    translators = models.ManyToManyField(
        'Person', related_name='books_translated', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Если gutenberg_id не указан (наша собственная книга), ставим 1000000 + id
        if not self.gutenberg_id:
            self.gutenberg_id = 1000000 + self.id
            Book.objects.filter(pk=self.pk).update(gutenberg_id=self.gutenberg_id)

    def __str__(self):
        if self.title:
            return self.title
        return str(self.id)

    def get_formats(self):
        return Format.objects.filter(book_id=self.id)

    def get_summaries(self):
        return Summary.objects.filter(book_id=self.id)


class Bookshelf(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


def book_file_path(instance, filename):
    folder = instance.book.gutenberg_id or instance.book.id or 'unsorted'
    return f'books_files/{folder}/{filename}'


class Format(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    mime_type = models.CharField(max_length=64)
    url = models.CharField(max_length=512, blank=True)
    file = models.FileField(upload_to=book_file_path, blank=True, null=True)

    def get_url(self):
        if self.file:
            return self.file.url
        return self.url

    def __str__(self):
        return f"{self.mime_type} ({self.book})"


class Language(models.Model):
    code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.code


class Person(models.Model):
    birth_year = models.SmallIntegerField(blank=True, null=True)
    death_year = models.SmallIntegerField(blank=True, null=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Summary(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        preview_len = 24
        return f'{self.text[:preview_len]}...' if len(self.text) > preview_len else self.text
        
class PageLine(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='lines')
    page_number = models.PositiveIntegerField()
    line_index = models.PositiveIntegerField()  # порядок строки на странице
    bbox_x0 = models.IntegerField()
    bbox_y0 = models.IntegerField()
    bbox_x1 = models.IntegerField()
    bbox_y1 = models.IntegerField()
    source_text = models.TextField()
    translated_ru = models.TextField(blank=True)
    translated_en = models.TextField(blank=True)

    class Meta:
        ordering = ['page_number', 'line_index']

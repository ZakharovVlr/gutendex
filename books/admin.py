from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, Bookshelf, Format, Language, Person, Subject, Summary


class FormatInline(admin.TabularInline):
    model = Format
    extra = 1
    fields = ('mime_type', 'file', 'url')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'gutenberg_id', 'title', 'download_count')
    search_fields = ('title', 'gutenberg_id')
    inlines = [FormatInline]


admin.site.register(Person)
admin.site.register(Language)
admin.site.register(Bookshelf)
admin.site.register(Subject)
admin.site.register(Summary)

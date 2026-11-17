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
    # Заменяем гигантские выпадающие списки на быстрый поиск по буквам:
    autocomplete_fields = ('authors', 'editors', 'translators', 'subjects', 'bookshelves')
    inlines = [FormatInline]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Bookshelf)
class BookshelfAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Language)
admin.site.register(Summary)


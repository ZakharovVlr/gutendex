import time
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from books.models import Book, Format


class Command(BaseCommand):
    help = 'Переносит обложки и файлы книг из Gutenberg в Cloudflare R2'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100, help='Сколько книг перенести за один запуск')

    def handle(self, *args, **options):
        limit = options['limit']
        # Берем самые популярные книги, у которых еще нет локального файла обложки в R2
        books = Book.objects.order_by('-download_count')[:limit]

        headers = {'User-Agent': 'Mozilla/5.0 (compatible; ColbookLibrary/1.0)'}

        for book in books:
            formats = Format.objects.filter(
                book=book,
                mime_type__in=['image/jpeg', 'text/html', 'application/epub+zip'],
                file=''
            )
            for fmt in formats:
                if not fmt.url or 'gutenberg.org' not in fmt.url:
                    continue
                try:
                    resp = requests.get(fmt.url, headers=headers, timeout=15)
                    resp.raise_for_status()

                    ext = 'jpg' if 'jpeg' in fmt.mime_type else ('epub' if 'epub' in fmt.mime_type else 'html')
                    filename = f"{book.gutenberg_id or book.id}_{ext}.{ext}"

                    fmt.file.save(filename, ContentFile(resp.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f'OK: {book.title[:30]} -> {filename}'))
                    time.sleep(0.3)  # Пауза, чтобы Gutenberg не банил за частые запросы
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Skip {fmt.url}: {e}'))

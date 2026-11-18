# books/management/commands/ingest_hocr.py
import re
import urllib.request

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from books.models import Book, PageLine


def parse_bbox(title: str):
    match = re.search(r'bbox (\d+) (\d+) (\d+) (\d+)', title or '')
    if not match:
        return None
    return tuple(int(x) for x in match.groups())


def read_source(path_or_url: str) -> str:
    if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
        with urllib.request.urlopen(path_or_url) as response:
            return response.read().decode('utf-8')
    with open(path_or_url, encoding='utf-8') as f:
        return f.read()


class Command(BaseCommand):
    help = 'Парсит hOCR-файл книги и сохраняет строки с координатами в БД'

    def add_arguments(self, parser):
        parser.add_argument('book_id', type=int)
        parser.add_argument('hocr_path', type=str)

    def handle(self, *args, **options):
        book = Book.objects.get(id=options['book_id'])
        soup = BeautifulSoup(read_source(options['hocr_path']), 'html.parser')

        PageLine.objects.filter(book=book).delete()
        created = 0

        for page_num, page in enumerate(soup.find_all(class_='ocr_page'), start=1):
            for line_idx, line in enumerate(page.find_all(class_='ocr_line')):
                bbox = parse_bbox(line.get('title', ''))
                if not bbox:
                    continue
                words = line.find_all(class_=re.compile(r'ocrx?_word'))
                text = ' '.join(w.get_text().strip() for w in words).strip()
                if not text:
                    continue
                PageLine.objects.create(
                    book=book,
                    page_number=page_num,
                    line_index=line_idx,
                    bbox_x0=bbox[0], bbox_y0=bbox[1],
                    bbox_x1=bbox[2], bbox_y1=bbox[3],
                    source_text=text,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано строк: {created}'))

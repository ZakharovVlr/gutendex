# books/management/commands/ingest_hocr.py
import re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from books.models import Book, PageLine

def parse_bbox(title: str) -> tuple[int, int, int, int] | None:
    match = re.search(r'bbox (\d+) (\d+) (\d+) (\d+)', title or '')
    if not match:
        return None
    return tuple(int(x) for x in match.groups())  # type: ignore[return-value]

class Command(BaseCommand):
    help = 'Парсит hOCR-файл книги и сохраняет строки с координатами в БД'

    def add_arguments(self, parser):
        parser.add_argument('book_id', type=int)
        parser.add_argument('hocr_path', type=str)

    def handle(self, *args, **options):
        book = Book.objects.get(id=options['book_id'])
        with open(options['hocr_path'], encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

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

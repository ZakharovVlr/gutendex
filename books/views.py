from django.db.models import Exists, OuterRef, Q

from rest_framework import exceptions as drf_exceptions, viewsets

from .models import *
from .serializers import *


class BookViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows books to be viewed. """

    lookup_field = 'gutenberg_id'

    queryset = Book.objects.exclude(download_count__isnull=True)
    queryset = queryset.exclude(title__isnull=True)

    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = self.queryset
        needs_distinct = False

        sort = self.request.GET.get('sort')
        if sort == 'ascending':
            queryset = queryset.order_by('id')
        elif sort == 'descending':
            queryset = queryset.order_by('-id')
        else:
            queryset = queryset.order_by('-download_count')

        author_year_end = self.request.GET.get('author_year_end')
        try:
            author_year_end = int(author_year_end)
        except:
            author_year_end = None
        if author_year_end is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__lte=author_year_end) |
                Q(authors__death_year__lte=author_year_end)
            )
            needs_distinct = True

        author_year_start = self.request.GET.get('author_year_start')
        try:
            author_year_start = int(author_year_start)
        except:
            author_year_start = None
        if author_year_start is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__gte=author_year_start) |
                Q(authors__death_year__gte=author_year_start)
            )
            needs_distinct = True

        copyright_parameter = self.request.GET.get('copyright')
        if copyright_parameter is not None:
            copyright_strings = copyright_parameter.split(',')
            copyright_values = set()
            for copyright_string in copyright_strings:
                if copyright_string == 'true':
                    copyright_values.add(True)
                elif copyright_string == 'false':
                    copyright_values.add(False)
                elif copyright_string == 'null':
                    copyright_values.add(None)
            for value in [True, False, None]:
                if value not in copyright_values:
                    queryset = queryset.exclude(copyright=value)

        id_string = self.request.GET.get('ids')
        if id_string is not None:
            ids = id_string.split(',')

            try:
                ids = [int(id) for id in ids]
            except ValueError:
                pass
            else:
                queryset = queryset.filter(gutenberg_id__in=ids)

        language_string = self.request.GET.get('languages')
        if language_string is not None:
            language_codes = [code.lower() for code in language_string.split(',')]
            language_subquery = Language.objects.filter(
                book=OuterRef('pk'),
                code__in=language_codes,
            )
            queryset = queryset.filter(Exists(language_subquery))

        mime_type = self.request.GET.get('mime_type')
        if mime_type is not None:
            queryset = queryset.filter(format__mime_type__startswith=mime_type)
            needs_distinct = True

        search_string = self.request.GET.get('search')
        if search_string is not None:
            search_string = search_string.replace('\x00', '')
            search_terms = search_string.split(' ')
            for term in search_terms[:4]:
                queryset = queryset.filter(
                    Q(authors__name__icontains=term) | Q(title__icontains=term)
                )
            needs_distinct = True

        topic = self.request.GET.get('topic')
        if topic is not None:
            bookshelf_subquery = Bookshelf.objects.filter(
                book=OuterRef('pk'),
                name__icontains=topic,
            )
            subject_subquery = Subject.objects.filter(
                book=OuterRef('pk'),
                name__icontains=topic,
            )
            queryset = queryset.filter(
                Exists(bookshelf_subquery) | Exists(subject_subquery)
            )

        if needs_distinct:
            return queryset.distinct()
        return queryset

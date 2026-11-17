import requests
from django.http import HttpResponse, HttpResponseBadRequest

ALLOWED_HOST = "www.gutenberg.org"


def proxy_image(request):
    image_url = request.GET.get('url')

    if not image_url:
        return HttpResponseBadRequest("Missing 'url' parameter")

    # Важная проверка безопасности: разрешаем проксировать
    # только картинки с gutenberg.org, а не любой произвольный сайт
    if ALLOWED_HOST not in image_url:
        return HttpResponseBadRequest("This host is not allowed")

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }

    try:
        response = requests.get(image_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return HttpResponse(status=502)  # Bad Gateway — не удалось получить картинку

    return HttpResponse(
        response.content,
        content_type=response.headers.get('Content-Type', 'image/jpeg')
    )

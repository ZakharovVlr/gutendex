from django.urls import include, path, re_path
from django.views.generic import TemplateView

from rest_framework import routers

from books import views
from books.proxy import proxy_image
from books.views import trigger_migration_view

router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='home.html')),
    re_path(r'^', include(router.urls)),
    re_path(r'^proxy-image/$', proxy_image, name='proxy-image'),
    path('trigger-migration/', trigger_migration_view),
]


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # Импортируем для мультиязычности

# 1. Сначала идут пути, которые НЕ ДОЛЖНЫ иметь префикса языка (технические)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), # Переключатель языков
    path("ckeditor5/", include('django_ckeditor_5.urls')), # Редактор
]

# 2. Основные разделы сайта, которые будут иметь префикс /en/, /es/ или /ru/
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    
    # Аутентификация (Allauth)
    path('accounts/', include('allauth.urls')),
    
    # Заказы
    path('orders/', include('apps.orders.urls')),

    # Каталог и главная страница
    path('', include('apps.catalog.urls', namespace='catalog')),
    
    prefix_default_language=False # Английский (default) будет без /en/, остальные с префиксом
)

# 3. Настройки для режима разработки (DEBUG=True)
if settings.DEBUG:
    # Раздача медиа-файлов
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
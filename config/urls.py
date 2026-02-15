from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Аутентификация
    path('accounts/', include('allauth.urls')),
    
    
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('orders/', include('apps.orders.urls')),

    # === ГЛАВНАЯ СТРАНИЦА ===
    # Мы говорим: "Все, что пришло на пустой адрес (''), ищи в apps.catalog.urls"
    path('', include('apps.catalog.urls')),
   
]

# Настройки для режима разработки (DEBUG=True)
if settings.DEBUG:
    # 1. Раздача медиа-файлов (картинок)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 2. Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
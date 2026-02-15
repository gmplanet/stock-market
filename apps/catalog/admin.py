from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from parler.admin import TranslatableAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from .models import Category, Product, ProductImage
from apps.warehouse.models import Stock, Warehouse

# --- РЕСУРС ИМПОРТА ---
class ProductResource(resources.ModelResource):
    # Поля файла (маленькие буквы)
    sku = fields.Field(attribute='sku', column_name='sku')
    price = fields.Field(attribute='price', column_name='price')
    is_active = fields.Field(attribute='is_active', column_name='is_active')
    
    # Виртуальное поле для количества
    quantity = fields.Field(column_name='quantity')

    class Meta:
        model = Product
        fields = ('id', 'sku', 'price', 'is_active', 'quantity')
        import_id_fields = ('sku',)
        skip_unchanged = True
        report_skipped = True

    # --- ЛОГИКА ---

    # 1. Исправляем ошибку 'file_name': добавляем **kwargs
    def before_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        """
        Перед сохранением: Если нет категории, ставим 'General'.
        """
        if not instance.category_id:
            # Ищем категорию General (по переводу), если нет - создаем
            cat = Category.objects.filter(translations__name='General').first()
            if not cat:
                cat = Category.objects.create(name='General', slug='general-def')
            instance.category = cat

    # 2. Исправляем ошибку 'file_name': добавляем **kwargs
    def after_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        """
        После сохранения: Обновляем остатки.
        """
        if dry_run:
            return
        
        # Получаем количество, которое библиотека временно положила в instance
        qty_val = getattr(instance, 'quantity', 0)
        
        # Ищем склад
        warehouse, _ = Warehouse.objects.get_or_create(name='Main Warehouse')

        try:
            qty = int(float(qty_val))
        except (ValueError, TypeError):
            qty = 0
            
        Stock.objects.update_or_create(
            product=instance,
            warehouse=warehouse,
            defaults={'quantity': qty}
        )

# --- АДМИНКА ---

class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    can_delete = False
    readonly_fields = ['available_quantity']
    # autocomplete_fields требует search_fields в ProductAdmin!
    autocomplete_fields = ['warehouse']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 80px;" />', obj.image.url) if obj.image else "-"

class CategoryAdmin(TranslatableAdmin, MPTTModelAdmin):
    list_display = ['name', 'is_active']
    # Добавляем поиск, чтобы Parler не ругался
    search_fields = ['translations__name']
    fieldsets = ((None, {'fields': ('parent', 'name', 'slug', 'description', 'image', 'is_active')}),)

@admin.register(Product)
class ProductAdmin(TranslatableAdmin, ImportExportModelAdmin):
    resource_class = ProductResource
    
    list_display = ['sku', 'name', 'price', 'total_stock', 'is_active']
    
    # ВАЖНО: search_fields нужен для работы StockInline
    search_fields = ['sku', 'translations__name']
    
    list_filter = ['is_active', 'category']
    inlines = [ProductImageInline, StockInline]
    
    def total_stock(self, obj):
        return sum(s.quantity for s in obj.stocks.all())

admin.site.register(Category, CategoryAdmin)
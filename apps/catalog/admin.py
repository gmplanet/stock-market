from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from mptt.admin import MPTTModelAdmin
from parler.admin import TranslatableAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
import random

from .models import Category, Product, ProductImage
from apps.warehouse.models import Stock, Warehouse

# --- Умный Ресурс (Импорт + Экспорт) ---
class ProductResource(resources.ModelResource):
    # 1. Настраиваем колонки. 
    # column_name='...' - это то, что будет в шапке Excel файла.
    
    sku = fields.Field(attribute='sku', column_name='SKU')
    price = fields.Field(attribute='price', column_name='Price')
    is_active = fields.Field(attribute='is_active', column_name='Active')
    
    # КАТЕГОРИЯ: Работаем как с текстом, чтобы читать/писать названия ("Phones"), а не ID.
    category_name = fields.Field(column_name='Category')
    
    # СКЛАД И КОЛИЧЕСТВО: Виртуальные поля (нет в модели Product, но нужны в файле)
    warehouse_name = fields.Field(column_name='Warehouse')
    quantity = fields.Field(column_name='Quantity')

    class Meta:
        model = Product
        # Список полей строго фиксируем. Никаких id или лишнего мусора.
        fields = ('sku', 'category_name', 'price', 'quantity', 'warehouse_name', 'is_active')
        export_order = ('sku', 'category_name', 'price', 'quantity', 'warehouse_name', 'is_active')
        import_id_fields = ('sku',) # Ищем товар по SKU
        skip_unchanged = True
        report_skipped = True

    # --- ЛОГИКА ЭКСПОРТА (Выгрузка из базы в Excel) ---
    
    def dehydrate_category_name(self, product):
        # Когда выгружаем в Excel, берем имя категории
        if product.category:
            return product.category.name  # Parler сам отдаст перевод
        return ""

    def dehydrate_warehouse_name(self, product):
        # По умолчанию пишем 'Main Warehouse'
        return "Main Warehouse"

    def dehydrate_quantity(self, product):
        # Считаем остатки для Excel
        return sum(stock.quantity for stock in product.stocks.all())

    # --- ЛОГИКА ИМПОРТА (Загрузка из Excel в базу) ---

    def before_import_row(self, row, **kwargs):
        """
        Чистим данные перед обработкой.
        """
        # Если в файле нет склада, ставим Main
        if not row.get('Warehouse'):
            row['Warehouse'] = 'Main Warehouse'
            
        # Убеждаемся, что склад существует в базе
        Warehouse.objects.get_or_create(name=row['Warehouse'])

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        САМОЕ ГЛАВНОЕ: Привязываем категорию ПЕРЕД сохранением.
        Решает ошибку NOT NULL constraint failed.
        """
        # 1. Достаем имя категории из нашего виртуального поля (оно временно легло в instance)
        # Если в файле пусто - берем 'General'
        cat_name = getattr(instance, 'category_name', 'General')
        if not cat_name:
            cat_name = 'General'
            
        # 2. Ищем или создаем категорию
        # Используем iexact для поиска без учета регистра
        category = Category.objects.filter(translations__name__iexact=cat_name).first()
        
        if not category:
            # Создаем новую
            slug_base = slugify(cat_name) or 'general'
            if Category.objects.filter(translations__slug=slug_base).exists():
                slug_base = f"{slug_base}-{random.randint(100, 999)}"
            category = Category.objects.create(name=cat_name, slug=slug_base)
            
        # 3. Железно привязываем категорию к товару
        instance.category = category

    def after_save_instance(self, instance, using_transactions, dry_run):
        """
        Обновляем остатки ПОСЛЕ сохранения товара.
        """
        if dry_run:
            return

        try:
            # Достаем данные, которые библиотека сохранила
            wh_name = getattr(instance, 'warehouse_name', 'Main Warehouse')
            qty = getattr(instance, 'quantity', 0)
            
            warehouse = Warehouse.objects.get(name=wh_name)
            
            # Превращаем "10.0" или "10" в число
            try:
                final_qty = int(float(qty))
            except (ValueError, TypeError):
                final_qty = 0

            Stock.objects.update_or_create(
                product=instance,
                warehouse=warehouse,
                defaults={'quantity': final_qty}
            )
        except Exception as e:
            print(f"Error saving stock: {e}")


# --- Настройки админки ---

class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    autocomplete_fields = ['warehouse']
    readonly_fields = ['available_quantity']
    can_delete = False

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px;" />', obj.image.url)
        return "-"

class CategoryAdmin(TranslatableAdmin, MPTTModelAdmin):
    list_display = ['name', 'is_active', 'image_preview']
    search_fields = ['translations__name']
    fieldsets = (
        (None, {'fields': ('parent', 'name', 'slug', 'description')}),
        ('Media', {'fields': ('image', 'image_preview')}),
        ('Settings', {'fields': ('is_active',)}),
    )
    readonly_fields = ['image_preview']
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"

@admin.register(Product)
class ProductAdmin(TranslatableAdmin, ImportExportModelAdmin):
    resource_class = ProductResource
    
    list_display = ['sku', 'name', 'price', 'total_stock', 'is_active', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'category']
    search_fields = ['sku', 'translations__name']
    
    fieldsets = (
        ('Basic Info', {'fields': ('sku', 'category', 'name', 'slug')}),
        ('Descriptions', {'fields': ('short_description', 'description')}),
        ('Media', {'fields': ('image', 'image_preview')}),
        ('Pricing', {'fields': ('price', 'compare_price')}),
        ('Settings', {'fields': ('is_active', 'is_featured')}),
    )
    
    readonly_fields = ['image_preview', 'total_stock']
    inlines = [ProductImageInline, StockInline]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"

    def total_stock(self, obj):
        return sum(stock.quantity for stock in obj.stocks.all())
    total_stock.short_description = 'Total Stock'

admin.site.register(Category, CategoryAdmin)
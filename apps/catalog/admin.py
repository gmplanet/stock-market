from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from parler.admin import TranslatableAdmin
from .models import Category, Product, ProductImage

# Исправляем конфликт метаклассов для MPTT + Parler
class CategoryAdmin(TranslatableAdmin, MPTTModelAdmin):
    """
    Admin for tree-like categories with translations.
    """
    list_display = ['name', 'is_active', 'image_preview']
    list_filter = ['is_active']
    # search_fields нужно указывать через translations__...
    search_fields = ['translations__name']
    
    fieldsets = (
        (None, {
            'fields': ('parent', 'name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = 'Preview'

class ProductImageInline(admin.TabularInline):
    """
    Inline gallery for products.
    """
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = 'Preview'

@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    """
    Advanced Product admin with tabs and gallery.
    """
    list_display = [
        'sku', 'name', 'category', 'price', 
        'is_active', 'image_preview'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['sku', 'translations__name']
    
    # Вкладки полей
    fieldsets = (
        ('Basic Info', {
            'fields': ('sku', 'category', 'name', 'slug')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description'),
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price'),
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    readonly_fields = ['image_preview']
    inlines = [ProductImageInline]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = 'Preview'

# Регистрируем категорию отдельно, так как она использует два класса админки
admin.site.register(Category, CategoryAdmin)
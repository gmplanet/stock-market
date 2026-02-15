from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from parler.admin import TranslatableAdmin

from .models import Category, Product, ProductImage
from apps.warehouse.models import Stock

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
class ProductAdmin(TranslatableAdmin):
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
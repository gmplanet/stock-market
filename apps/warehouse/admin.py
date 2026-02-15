from django.contrib import admin
from .models import Warehouse, Stock

class StockInline(admin.TabularInline):
    """
    Позволяет редактировать остатки прямо внутри Склада.
    """
    model = Stock
    extra = 1 # Одна пустая строка для добавления
    autocomplete_fields = ['product'] # Чтобы искать товар, а не листать список

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'is_active']
    search_fields = ['name']
    inlines = [StockInline] # Вкладка с товарами внутри склада

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reserved', 'available_quantity']
    list_filter = ['warehouse']
    search_fields = ['product__sku', 'product__translations__name']
    autocomplete_fields = ['product', 'warehouse']
    # available_quantity - это свойство, его нельзя редактировать, но можно показывать
    readonly_fields = ['available_quantity']
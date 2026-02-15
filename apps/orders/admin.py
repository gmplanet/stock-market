from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Чтобы не грузить выпадающий список из 1000 товаров
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_cost', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['total_cost']
    
    # total_cost - это свойство, а не поле БД, поэтому его нужно добавить вручную для отображения
    def total_cost(self, obj):
        return obj.total_cost
    total_cost.short_description = 'Total Cost'
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product

class Warehouse(models.Model):
    """
    Физический склад или магазин.
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    priority = models.IntegerField(default=0, verbose_name=_('Priority'), help_text=_('Higher priority warehouses are used first for shipping'))

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name

class Stock(models.Model):
    """
    Количество конкретного товара на конкретном складе.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks', verbose_name=_('Warehouse'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks', verbose_name=_('Product'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    
    # Резерв (на случай, если товар в корзине, но еще не оплачен)
    reserved = models.PositiveIntegerField(default=0, verbose_name=_('Reserved'))

    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        # Нельзя дублировать записи: один товар на одном складе — одна запись
        unique_together = ['warehouse', 'product'] 

    def __str__(self):
        return f"{self.product.sku} - {self.warehouse.name} ({self.quantity})"
    
    @property
    def available_quantity(self):
        """Реально доступное количество (Физическое - Резерв)"""
        return max(0, self.quantity - self.reserved)
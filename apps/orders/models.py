from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product
from apps.core.models import BaseModel

class Order(BaseModel):
    """
    Заказ пользователя.
    """
    STATUS_CHOICES = (
        ('new', _('New')),
        ('confirmed', _('Confirmed')),
        ('paid', _('Paid')),
        ('shipped', _('Shipped')),
        ('canceled', _('Canceled')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name=_('User'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_('Status'))
    
    # Контакты для доставки (копируются из профиля, но могут быть изменены для конкретного заказа)
    first_name = models.CharField(max_length=50, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=50, verbose_name=_('Last Name'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'))
    address = models.TextField(verbose_name=_('Delivery Address'))
    
    note = models.TextField(blank=True, verbose_name=_('Note'))
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

    @property
    def total_cost(self):
        return sum(item.total_cost for item in self.items.all())

class OrderItem(models.Model):
    """
    Товар внутри заказа. 
    Мы храним цену отдельно, так как цена товара в каталоге может измениться, 
    а в старом заказе она должна остаться прежней.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name=_('Product'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.quantity}x {self.product.sku}"

    @property
    def total_cost(self):
        return self.price * self.quantity
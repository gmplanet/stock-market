from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from parler.models import TranslatedFields
from parler.managers import TranslatableManager, TranslatableQuerySet
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseTranslatableModel



# 1. Создаем гибридный QuerySet (объединяем переводы и дерево)
class CategoryQuerySet(TranslatableQuerySet, TreeQuerySet):
    def as_manager(self):
        return CategoryManager.from_queryset(type(self))()


# 2. Создаем гибридный Manager
class CategoryManager(TreeManager, TranslatableManager):
    queryset_class = CategoryQuerySet
    
    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)


class Category(MPTTModel, BaseTranslatableModel):
    """
    Tree-like product categories (MPTT + Parler).
    """
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_('Parent category')
    )
    
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        slug=models.SlugField(max_length=255, unique=True, verbose_name=_('Slug')),
        # Было: description=RichTextUploadingField(...)
        # Стало:
        description=CKEditor5Field(
            blank=True, 
            config_name='extends',
            verbose_name=_('Description')
        ),
    )
    
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('Image'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    # 3. Подключаем наш гибридный менеджер
    objects = CategoryManager()
    
    class MPTTMeta:
        order_insertion_by = ['is_active']
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f"Category {self.id}"

class Product(BaseTranslatableModel):
    """
    Products with translations and price variations.
    """
    category = TreeForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name=_('Category')
    )
    sku = models.CharField(max_length=100, unique=True, verbose_name=_('SKU'))
    
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        slug=models.SlugField(max_length=255, unique=True, verbose_name=_('Slug')),
        description=CKEditor5Field(
            blank=True, 
            config_name='extends',
            verbose_name=_('Full description'),
        ),
        short_description=models.CharField(
            max_length=500, 
            blank=True,
            verbose_name=_('Short description')
        ),
    )
    
    image = models.ImageField(
        upload_to='products/', 
        blank=True, 
        null=True,
        verbose_name=_('Main image')
    )
    
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    compare_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name=_('Compare at price')
    )
    
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Featured'))
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'is_featured']),
        ]
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or self.sku
    
    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

class ProductImage(models.Model):
    """
    Product image gallery.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('Product'))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_('Image'))
    
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 80}
    )
    
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_('Alt text'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
    
    def __str__(self):
        return f"Image for {self.product.sku}"
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel

class BaseModel(models.Model):
    """
    Abstract base model.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    
    class Meta:
        abstract = True

class BaseTranslatableModel(TranslatableModel, BaseModel):
    """
    Abstract model with translation support.
    """
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            
            # Default slug generation logic
            for language in ['en', 'es', 'ru']:
                self.set_current_language(language)
                try:
                    if hasattr(self, 'slug') and not self.slug:
                        title_text = self.safe_translation_getter('name') or self.safe_translation_getter('title')
                        if title_text:
                            self.slug = slugify(title_text)
                            self.save_translation(self.get_current_language_model())
                except:
                    pass
        
        super().save(*args, **kwargs)
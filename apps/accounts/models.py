from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model.
    Login via email instead of username.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone number'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class UserProfile(models.Model):
    """
    User profile with additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('User'))
    company_name = models.CharField(max_length=255, blank=True, verbose_name=_('Company name'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
    
    def __str__(self):
        return f"Profile {self.user.email}"
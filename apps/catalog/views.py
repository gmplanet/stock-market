from django.shortcuts import render
from .models import Product

def home(request):
    """
    Главная страница: показывает список всех товаров.
    """
    # Берем все активные товары
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'page_title': 'Home - Stock Market'
    }
    
    return render(request, 'catalog/home.html', context)
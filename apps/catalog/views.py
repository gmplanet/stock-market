from django.shortcuts import render
from .models import Product

def product_list(request):
    # Fetching only active products to show on the storefront
    products = Product.objects.filter(is_active=True).order_by('-id')
    return render(request, 'catalog/product_list.html', {
        'products': products
    })
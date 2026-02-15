from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.catalog.models import Product
from .models import Order, OrderItem

@login_required
def add_to_cart(request, product_id):
    # 1. Ищем товар
    product = get_object_or_404(Product, id=product_id)
    
    # 2. Ищем или создаем черновик заказа для текущего пользователя
    # Мы используем get_or_create: если есть заказ со статусом 'new', берем его.
    # Если нет — создаем новый.
    order, created = Order.objects.get_or_create(
        user=request.user, 
        status='new',
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': ''
        }
    )
    
    # 3. Ищем, есть ли уже этот товар в заказе
    item, created = OrderItem.objects.get_or_create(
        order=order, 
        product=product,
        defaults={'price': product.price} # Если создаем, берем текущую цену
    )
    
    # 4. Если товар уже был, просто увеличиваем количество
    if not created:
        item.quantity += 1
        item.save()
        
    # 5. Возвращаем пользователя обратно на витрину
    return redirect('catalog:home')
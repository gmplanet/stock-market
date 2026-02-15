from django.urls import path
from .views import add_to_cart

app_name = 'orders'

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
]
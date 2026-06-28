from django.contrib import admin
from .models import Cart, CartItems, Item, OrderPlaced


admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(OrderPlaced)
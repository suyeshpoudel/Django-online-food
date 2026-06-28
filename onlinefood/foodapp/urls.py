from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name="login_page"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_page, name="logout_page"),
    path('add-cart/<item_uid>', views.add_cart, name='add_cart'),
    path('cart/', views.cart, name="cart"),
    path('remove_cart_items/<cart_item_uid>', views.remove_cart_items, name="remove_cart_items"),
    path('orders/', views.orders, name='orders'),
    path('add-item/', views.add_item, name='add_item'),
    path('all-items/', views.all_items, name='all_items'),
    path('delete-recipe/<item_uid>/', views.delete_item, name="delete_item"),
    path('update-recipe/<item_uid>/', views.update_item, name="update_item"),
    path('success/', views.success, name="success"),
    path('all-orders/', views.all_orders, name="all_orders"),
]

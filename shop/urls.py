from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.shop_home,      name='shop_home'),
    path('catalog/',              views.shop_catalog,   name='shop_catalog'),
    path('product/<int:pk>/',     views.product_detail, name='product_detail'),
    path('cart/',                 views.cart_view,      name='cart_view'),
    path('cart/add/<int:pk>/',    views.cart_add,       name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove,    name='cart_remove'),
    path('cart/update/<int:pk>/', views.cart_update,    name='cart_update'),
    path('checkout/',             views.checkout,       name='checkout'),
    path('confirm/<str:code>/',   views.order_confirm,  name='order_confirm'),
    path('track/',                views.order_track,    name='order_track'),
]

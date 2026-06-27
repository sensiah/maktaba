from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.dashboard,            name='dashboard'),
    path('products/',                      views.product_list,         name='product_list'),
    path('products/add/',                  views.product_create,       name='product_create'),
    path('products/<int:pk>/edit/',        views.product_edit,         name='product_edit'),
    path('products/<int:pk>/delete/',      views.product_delete,       name='product_delete'),
    path('products/<int:pk>/stock/',       views.stock_adjustment,     name='stock_adjustment'),
    path('products/<int:pk>/barcode/',     views.barcode_single,       name='barcode_single'),
    path('customers/',                     views.customer_list,        name='customer_list'),
    path('customers/add/',                 views.customer_create,      name='customer_create'),
    path('customers/<int:pk>/edit/',       views.customer_edit,        name='customer_edit'),
    path('customers/<int:pk>/',            views.customer_detail,      name='customer_detail'),
    path('orders/',                        views.order_list,           name='order_list'),
    path('orders/new/',                    views.order_create,         name='order_create'),
    path('orders/<int:pk>/',               views.order_detail,         name='order_detail'),
    path('orders/<int:pk>/cancel/',        views.order_cancel,         name='order_cancel'),
    path('online-orders/',                 views.online_order_list,    name='online_order_list'),
    path('online-orders/<int:pk>/',        views.online_order_detail,  name='online_order_detail'),
    path('online-orders/<int:pk>/status/', views.online_order_status,  name='online_order_status'),
    path('reports/',                       views.reports,              name='reports'),
    path('barcodes/',                      views.barcode_sheet,        name='barcode_sheet'),
    path('api/products/',                  views.product_search_api,   name='product_search_api'),
    path('api/barcode/',                   views.barcode_lookup_api,   name='barcode_lookup_api'),
]

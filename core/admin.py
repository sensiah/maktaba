from django.contrib import admin
from .models import Product, Category, Customer, Order, OrderItem, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock_quantity', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'total_purchases']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'cashier', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method']
    inlines = [OrderItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'created_by', 'created_at']

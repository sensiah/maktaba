from django.contrib import admin
from .models import OnlineOrder, OnlineOrderItem, ProductReview


class ItemInline(admin.TabularInline):
    model         = OnlineOrderItem
    extra         = 0
    readonly_fields = ['product', 'quantity', 'unit_price']


@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display   = ['tracking_code', 'customer_name', 'customer_phone', 'neighbourhood', 'total_amount', 'status', 'created_at']
    list_filter    = ['status']
    search_fields  = ['tracking_code', 'customer_name', 'customer_phone']
    readonly_fields = ['tracking_code', 'created_at']
    inlines        = [ItemInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating', 'created_at']

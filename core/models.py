from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name                = models.CharField(max_length=200)
    category            = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sku                 = models.CharField(max_length=50, unique=True)
    price               = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity      = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    description         = models.TextField(blank=True)
    is_active           = models.BooleanField(default=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class Customer(models.Model):
    name            = models.CharField(max_length=200)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    address         = models.TextField(blank=True)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'معلق'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغى'),
        ('refunded',  'مسترجع'),
    ]
    PAYMENT_CHOICES = [
        ('cash',     'نقداً'),
        ('card',     'بطاقة'),
        ('transfer', 'تحويل'),
    ]
    customer       = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    cashier        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب #{self.id}"

    @property
    def final_amount(self):
        return self.total_amount - self.discount


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class StockMovement(models.Model):
    TYPES = [('in','إدخال'),('out','إخراج'),('adjustment','تعديل')]
    product      = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type= models.CharField(max_length=20, choices=TYPES)
    quantity     = models.IntegerField()
    reason       = models.CharField(max_length=200, blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

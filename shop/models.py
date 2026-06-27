from django.db import models
from core.models import Product

NEIGHBOURHOODS = [
    ('', 'اختر الحي'),
    ('المركز', 'المركز'),
    ('حي النصر', 'حي النصر'),
    ('حي الشهداء', 'حي الشهداء'),
    ('حي 1 نوفمبر', 'حي 1 نوفمبر'),
    ('حي السلام', 'حي السلام'),
    ('حي الفتح', 'حي الفتح'),
    ('حي التوفيق', 'حي التوفيق'),
    ('حي البدر', 'حي البدر'),
    ('حي الوحدة', 'حي الوحدة'),
    ('حي الأمل', 'حي الأمل'),
    ('حي الزيتون', 'حي الزيتون'),
    ('حي آخر', 'حي آخر'),
]


class OnlineOrder(models.Model):
    STATUS_CHOICES = [
        ('pending',    'في الانتظار'),
        ('confirmed',  'مؤكد'),
        ('processing', 'قيد التحضير'),
        ('out',        'المندوب في الطريق'),
        ('delivered',  'تم التسليم'),
        ('cancelled',  'ملغى'),
    ]

    customer_name  = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    neighbourhood  = models.CharField(max_length=100)
    address        = models.TextField()
    notes          = models.TextField(blank=True)

    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tracking_code  = models.CharField(max_length=20, unique=True, blank=True)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب إلكتروني'
        verbose_name_plural = 'الطلبات الإلكترونية'

    def __str__(self):
        return f"طلب #{self.tracking_code} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            import random, string
            self.tracking_code = 'MT' + ''.join(random.choices(string.digits, k=7))
        super().save(*args, **kwargs)


class OnlineOrderItem(models.Model):
    order      = models.ForeignKey(OnlineOrder, related_name='items', on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class ProductReview(models.Model):
    product    = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    name       = models.CharField(max_length=100)
    rating     = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.product.name} ({self.rating}★)"

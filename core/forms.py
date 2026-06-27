from django import forms
from .models import Product, Customer, Order, OrderItem, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'price', 'cost_price',
                  'stock_quantity', 'low_stock_threshold', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'payment_method', 'discount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem,
    fields=['product', 'quantity', 'unit_price'],
    extra=1, can_delete=True
)


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'reason']
        widgets = {
            'reason': forms.TextInput(attrs={'placeholder': 'e.g. Restock from supplier'}),
        }

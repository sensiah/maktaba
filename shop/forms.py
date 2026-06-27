from django import forms
from .models import OnlineOrder, ProductReview, NEIGHBOURHOODS


class CheckoutForm(forms.ModelForm):
    neighbourhood = forms.ChoiceField(choices=NEIGHBOURHOODS, label='الحي')

    class Meta:
        model  = OnlineOrder
        fields = ['customer_name', 'customer_phone', 'customer_email', 'neighbourhood', 'address', 'notes']
        labels = {
            'customer_name':  'الاسم الكامل',
            'customer_phone': 'رقم الهاتف',
            'customer_email': 'البريد الإلكتروني (اختياري)',
            'address':        'العنوان التفصيلي',
            'notes':          'ملاحظات للمندوب (اختياري)',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'الشارع، رقم المبنى، معلم قريب...'}),
            'notes':   forms.Textarea(attrs={'rows': 2}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model   = ProductReview
        fields  = ['name', 'rating', 'comment']
        labels  = {'name': 'اسمك', 'rating': 'التقييم', 'comment': 'تعليقك'}
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}

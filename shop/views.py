from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from core.models import Product, Category
from .models import OnlineOrder, OnlineOrderItem, ProductReview
from .forms import CheckoutForm, ReviewForm

DELIVERY_FEE = 200
CITY = 'متليلي الشعانبة'


def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def cart_totals(cart):
    items    = []
    subtotal = 0
    for pid, data in cart.items():
        try:
            product = Product.objects.get(pk=int(pid), is_active=True)
            qty     = int(data['qty'])
            line    = qty * float(product.price)
            items.append({'product': product, 'qty': qty, 'subtotal': line})
            subtotal += line
        except Product.DoesNotExist:
            pass
    return items, subtotal


# ── Pages ──────────────────────────────────────────────────────────────────

def shop_home(request):
    categories   = Category.objects.all()
    featured     = Product.objects.filter(is_active=True, stock_quantity__gt=0).order_by('-created_at')[:8]
    new_arrivals = Product.objects.filter(is_active=True, stock_quantity__gt=0).order_by('-created_at')[:4]
    return render(request, 'shop/home.html', {
        'categories': categories, 'featured': featured, 'new_arrivals': new_arrivals,
    })


def shop_catalog(request):
    q          = request.GET.get('q', '')
    cat_id     = request.GET.get('cat', '')
    sort       = request.GET.get('sort', 'newest')
    products   = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    categories = Category.objects.all()

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat_id:
        products = products.filter(category_id=cat_id)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    selected_cat = Category.objects.filter(pk=cat_id).first() if cat_id else None
    return render(request, 'shop/catalog.html', {
        'products': products, 'categories': categories,
        'q': q, 'cat_id': cat_id, 'sort': sort, 'selected_cat': selected_cat,
    })


def product_detail(request, pk):
    product    = get_object_or_404(Product, pk=pk, is_active=True)
    reviews    = product.reviews.order_by('-created_at')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    related    = Product.objects.filter(category=product.category, is_active=True, stock_quantity__gt=0).exclude(pk=pk)[:4]
    form       = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.product = product
            r.save()
            messages.success(request, 'شكراً! تم إضافة تعليقك.')
            return redirect('product_detail', pk=pk)

    return render(request, 'shop/product_detail.html', {
        'product': product, 'reviews': reviews,
        'avg_rating': avg_rating, 'related': related, 'form': form,
    })


# ── Cart ──────────────────────────────────────────────────────────────────

def cart_view(request):
    cart             = get_cart(request)
    items, subtotal  = cart_totals(cart)
    total            = subtotal + DELIVERY_FEE if items else 0
    return render(request, 'shop/cart.html', {
        'items': items, 'subtotal': subtotal,
        'delivery_fee': DELIVERY_FEE, 'total': total,
    })


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart    = get_cart(request)
    pid     = str(pk)
    qty     = int(request.POST.get('qty', 1))

    if pid in cart:
        cart[pid]['qty'] = min(cart[pid]['qty'] + qty, product.stock_quantity)
    else:
        cart[pid] = {'qty': min(qty, product.stock_quantity)}

    save_cart(request, cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = sum(i['qty'] for i in cart.values())
        return JsonResponse({'ok': True, 'cart_count': count})

    messages.success(request, f'تمت إضافة «{product.name}» إلى السلة.')
    return redirect(request.META.get('HTTP_REFERER', 'shop_catalog'))


def cart_remove(request, pk):
    cart = get_cart(request)
    cart.pop(str(pk), None)
    save_cart(request, cart)
    return redirect('cart_view')


def cart_update(request, pk):
    cart = get_cart(request)
    pid  = str(pk)
    qty  = int(request.POST.get('qty', 1))
    if qty < 1:
        cart.pop(pid, None)
    else:
        product      = get_object_or_404(Product, pk=pk)
        cart[pid]    = {'qty': min(qty, product.stock_quantity)}
    save_cart(request, cart)
    return redirect('cart_view')


# ── Checkout ──────────────────────────────────────────────────────────────

def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('cart_view')

    items, subtotal = cart_totals(cart)
    total = subtotal + DELIVERY_FEE

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order              = form.save(commit=False)
            order.total_amount = total
            order.save()

            for item in items:
                OnlineOrderItem.objects.create(
                    order      = order,
                    product    = item['product'],
                    quantity   = item['qty'],
                    unit_price = item['product'].price,
                )
                item['product'].stock_quantity -= item['qty']
                item['product'].save()

            save_cart(request, {})
            return redirect('order_confirm', code=order.tracking_code)
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'form': form, 'items': items,
        'subtotal': subtotal, 'delivery_fee': DELIVERY_FEE, 'total': total,
        'city': CITY,
    })


def order_confirm(request, code):
    order = get_object_or_404(OnlineOrder, tracking_code=code)
    return render(request, 'shop/order_confirm.html', {'order': order})


def order_track(request):
    order = None
    code  = request.GET.get('code', '').strip()
    if code:
        try:
            order = OnlineOrder.objects.get(tracking_code=code)
        except OnlineOrder.DoesNotExist:
            messages.error(request, 'رمز التتبع غير صحيح.')
    return render(request, 'shop/order_track.html', {'order': order, 'code': code})

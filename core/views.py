from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
from .models import Product, Category, Customer, Order, OrderItem, StockMovement
from .forms import ProductForm, CustomerForm, OrderForm, OrderItemFormSet, StockMovementForm


def is_admin(user):
    return user.is_staff or user.is_superuser


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    today_sales = Order.objects.filter(
        created_at__date=today, status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    month_sales = Order.objects.filter(
        created_at__date__gte=month_start, status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    total_products = Product.objects.filter(is_active=True).count()
    low_stock = Product.objects.filter(is_active=True, stock_quantity__lte=10)
    total_customers = Customer.objects.count()
    recent_orders = Order.objects.order_by('-created_at')[:8]

    # Sales last 7 days for chart
    sales_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        amount = Order.objects.filter(
            created_at__date=day, status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.append({'day': day.strftime('%a'), 'amount': float(amount)})

    context = {
        'today_sales': today_sales,
        'month_sales': month_sales,
        'total_products': total_products,
        'low_stock': low_stock,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'sales_data': sales_data,
    }
    return render(request, 'core/dashboard.html', context)


# ─── Products ────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    products = Product.objects.filter(is_active=True).select_related('category')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    return render(request, 'core/product_list.html', {
        'products': products, 'categories': categories,
        'query': query, 'selected_category': category_id
    })


@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    messages.success(request, f'"{product.name}" removed.')
    return redirect('product_list')


@login_required
@user_passes_test(is_admin)
def stock_adjustment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.product = product
            movement.created_by = request.user
            movement.save()
            if movement.movement_type == 'in':
                product.stock_quantity += movement.quantity
            elif movement.movement_type == 'out':
                product.stock_quantity -= movement.quantity
            else:
                product.stock_quantity = movement.quantity
            product.save()
            messages.success(request, 'Stock updated.')
            return redirect('product_list')
    else:
        form = StockMovementForm()
    return render(request, 'core/stock_form.html', {'form': form, 'product': product})


# ─── Customers ───────────────────────────────────────────────────────────────

@login_required
def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query))
    return render(request, 'core/customer_list.html', {'customers': customers, 'query': query})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added.')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated.')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'core/customer_detail.html', {'customer': customer, 'orders': orders})


# ─── Orders ──────────────────────────────────────────────────────────────────

@login_required
def order_list(request):
    status = request.GET.get('status', '')
    orders = Order.objects.select_related('customer', 'cashier').order_by('-created_at')
    if status:
        orders = orders.filter(status=status)
    return render(request, 'core/order_list.html', {'orders': orders, 'status_filter': status})


@login_required
def order_create(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        customer_id = request.POST.get('customer')
        payment_method = request.POST.get('payment_method', 'cash')
        discount = float(request.POST.get('discount', 0))
        notes = request.POST.get('notes', '')

        if not product_ids:
            messages.error(request, 'Please add at least one product.')
            return redirect('order_create')

        customer = Customer.objects.filter(pk=customer_id).first() if customer_id else None

        order = Order.objects.create(
            customer=customer,
            cashier=request.user,
            payment_method=payment_method,
            discount=discount,
            notes=notes,
            status='completed'
        )

        total = 0
        for pid, qty in zip(product_ids, quantities):
            try:
                product = Product.objects.get(pk=pid, is_active=True)
                qty = int(qty)
                if qty > 0:
                    OrderItem.objects.create(
                        order=order, product=product,
                        quantity=qty, unit_price=product.price
                    )
                    product.stock_quantity -= qty
                    product.save()
                    total += product.price * qty
            except (Product.DoesNotExist, ValueError):
                continue

        order.total_amount = total
        order.save()

        if customer:
            customer.total_purchases += order.final_amount
            customer.save()

        messages.success(request, f'Order #{order.id} completed!')
        return redirect('order_detail', pk=order.pk)

    products = Product.objects.filter(is_active=True, stock_quantity__gt=0).select_related('category')
    customers = Customer.objects.all()
    return render(request, 'core/order_create.html', {'products': products, 'customers': customers})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product')
    return render(request, 'core/order_detail.html', {'order': order, 'items': items})


@login_required
@user_passes_test(is_admin)
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'completed':
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} cancelled and stock restored.')
    return redirect('order_list')


# ─── Reports ─────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def reports(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    total_revenue = Order.objects.filter(status='completed').aggregate(t=Sum('total_amount'))['t'] or 0
    month_revenue = Order.objects.filter(status='completed', created_at__date__gte=month_start).aggregate(t=Sum('total_amount'))['t'] or 0
    total_orders = Order.objects.filter(status='completed').count()
    month_orders = Order.objects.filter(status='completed', created_at__date__gte=month_start).count()

    top_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'), revenue=Sum('unit_price'))
        .order_by('-total_sold')[:10]
    )

    monthly_sales = []
    for month in range(1, today.month + 1):
        start = today.replace(month=month, day=1)
        if month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=month + 1, day=1)
        revenue = Order.objects.filter(
            status='completed',
            created_at__date__gte=start,
            created_at__date__lt=end
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        monthly_sales.append({'month': start.strftime('%b'), 'revenue': float(revenue)})

    low_stock_products = Product.objects.filter(is_active=True, stock_quantity__lte=10).order_by('stock_quantity')

    context = {
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'total_orders': total_orders,
        'month_orders': month_orders,
        'top_products': top_products,
        'monthly_sales': monthly_sales,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'core/reports.html', context)


# ─── API for product search ───────────────────────────────────────────────────

@login_required
def product_search_api(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(
        is_active=True, stock_quantity__gt=0,
        name__icontains=q
    ).values('id', 'name', 'price', 'stock_quantity', 'sku')[:10]
    return JsonResponse({'products': list(products)})


@login_required
def barcode_lookup_api(request):
    """Look up a product by its SKU (barcode value)."""
    sku = request.GET.get('sku', '').strip()
    try:
        product = Product.objects.get(sku=sku, is_active=True)
        return JsonResponse({
            'found': True,
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock_quantity': product.stock_quantity,
            'sku': product.sku,
        })
    except Product.DoesNotExist:
        return JsonResponse({'found': False, 'message': f'No product found for barcode: {sku}'})


@login_required
@user_passes_test(is_admin)
def barcode_sheet(request):
    """Generate a printable barcode sheet for all active products."""
    products = Product.objects.filter(is_active=True).order_by('name')
    return render(request, 'core/barcode_sheet.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def barcode_single(request, pk):
    """Generate barcode for a single product."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/barcode_sheet.html', {'products': [product]})


# ─── Online Orders Management ────────────────────────────────────────────────

@login_required
def online_order_list(request):
    from shop.models import OnlineOrder
    status = request.GET.get('status', '')
    orders = OnlineOrder.objects.all()
    if status:
        orders = orders.filter(status=status)
    pending_count = OnlineOrder.objects.filter(status='pending').count()
    return render(request, 'core/online_order_list.html', {
        'orders': orders, 'status_filter': status, 'pending_count': pending_count
    })


@login_required
def online_order_detail(request, pk):
    from shop.models import OnlineOrder
    order = get_object_or_404(OnlineOrder, pk=pk)
    items = order.items.select_related('product')
    return render(request, 'core/online_order_detail.html', {'order': order, 'items': items})


@login_required
@user_passes_test(is_admin)
def online_order_status(request, pk):
    from shop.models import OnlineOrder
    order = get_object_or_404(OnlineOrder, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in OnlineOrder.STATUS_CHOICES]
        if new_status in valid:
            order.status = new_status
            order.save()
            messages.success(request, f'تم تحديث حالة الطلب #{order.tracking_code}')
    return redirect('online_order_detail', pk=pk)

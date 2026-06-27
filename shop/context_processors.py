def cart(request):
    cart  = request.session.get('cart', {})
    count = sum(item['qty'] for item in cart.values())
    return {'cart_count': count}

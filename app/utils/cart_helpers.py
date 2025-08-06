

def get_cart_data(session):
    cart = session.get('cart', {})
    
    total_items = sum(item['quantity'] for item in cart.values())
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    discount = subtotal * 0.33  # Example 33% discount
    total = subtotal - discount
    
    return {
        'items': cart,
        'total_items': total_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total
    }
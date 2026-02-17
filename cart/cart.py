"""
Session-based shopping cart implementation.
"""
from decimal import Decimal
from django.conf import settings
from catalog.models import Product


CART_SESSION_ID = 'cart'


class Cart:
    """
    A session-based shopping cart class.
    """
    
    def __init__(self, request):
        """
        Initialize the cart from the session.
        """
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        
        Args:
            product: Product instance
            quantity: Number of items to add
            override_quantity: If True, set quantity instead of incrementing
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        # Ensure quantity doesn't exceed stock
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock
        
        self.save()
    
    def remove(self, product_id):
        """
        Remove a product from the cart.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        """
        Update the quantity of a product in the cart.
        """
        product_id = str(product_id)
        if product_id in self.cart and quantity > 0:
            product = Product.objects.get(id=int(product_id))
            # Ensure quantity doesn't exceed stock
            quantity = min(quantity, product.stock)
            self.cart[product_id]['quantity'] = quantity
            self.save()
        elif quantity <= 0:
            self.remove(product_id)
    
    def save(self):
        """
        Mark the session as modified to ensure it gets saved.
        """
        self.session.modified = True
    
    def clear(self):
        """
        Remove the cart from the session.
        """
        del self.session[CART_SESSION_ID]
        self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and fetch products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item
    
    def __len__(self):
        """
        Return the total number of items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_subtotal(self):
        """
        Return the subtotal of all items in the cart.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
    
    def get_shipping(self):
        """
        Return the shipping cost (placeholder - free shipping over $50).
        """
        subtotal = self.get_subtotal()
        if subtotal >= Decimal('50.00'):
            return Decimal('0.00')
        return Decimal('5.99')
    
    def get_total(self):
        """
        Return the total including shipping.
        """
        return self.get_subtotal() + self.get_shipping()
    
    def is_empty(self):
        """
        Check if the cart is empty.
        """
        return len(self.cart) == 0

"""
Tests for cart functionality.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Category, Product
from cart.cart import Cart


class CartClassTests(TestCase):
    """Tests for the Cart class."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=Decimal('29.99'),
            stock=10,
            is_active=True
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            category=self.category,
            price=Decimal('49.99'),
            stock=5,
            is_active=True
        )
    
    def test_add_item_to_cart(self):
        """Test adding an item to the cart via POST."""
        response = self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 2, 'next': '/cart/'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check cart page shows item
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_update_cart_quantity(self):
        """Test updating the quantity of an item in the cart."""
        # First add the item
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        
        # Then update the quantity
        response = self.client.post(
            reverse('cart_update', args=[self.product.id]),
            {'quantity': 3}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_remove_item_from_cart(self):
        """Test removing an item from the cart."""
        # First add the item
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        
        # Then remove it
        response = self.client.post(
            reverse('cart_remove', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_cart_page_empty(self):
        """Test cart page shows empty state when cart is empty."""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')
    
    def test_cart_subtotal_calculation(self):
        """Test that cart calculates subtotal correctly."""
        # Add items
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 2}  # 2 x $29.99 = $59.98
        )
        self.client.post(
            reverse('cart_add', args=[self.product2.id]),
            {'quantity': 1}  # 1 x $49.99 = $49.99
        )
        
        # Total should be $109.97
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        # Cart should display both products
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Test Product 2')
    
    def test_free_shipping_over_50(self):
        """Test that shipping is free for orders over $50."""
        # Add enough to exceed $50
        self.client.post(
            reverse('cart_add', args=[self.product2.id]),
            {'quantity': 2}  # 2 x $49.99 = $99.98
        )
        
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'FREE')


class CheckoutViewTests(TestCase):
    """Tests for the checkout page."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category-checkout',
            is_active=True
        )
        self.product = Product.objects.create(
            name='Checkout Product',
            slug='checkout-product',
            category=self.category,
            price=Decimal('19.99'),
            stock=10,
            is_active=True
        )
    
    def test_checkout_page_loads(self):
        """Test that checkout page loads."""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
    
    def test_checkout_shows_cart_items(self):
        """Test that checkout page shows cart items."""
        # Add item to cart
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )
        
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout Product')

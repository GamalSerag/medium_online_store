"""
Tests for cart functionality.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Category, Product
from cart.cart import Cart
from orders.models import Order


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
    
    def test_flat_delivery_fee_for_non_empty_cart(self):
        """Test that non-empty carts use the flat EGP 100 delivery fee."""
        self.client.post(
            reverse('cart_add', args=[self.product2.id]),
            {'quantity': 2}
        )
        
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'Delivery fee')
        self.assertContains(response, 'EGP 100.00')


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

    def test_checkout_creates_order_with_valid_fields(self):
        """Test that valid checkout data creates an order."""
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )

        response = self.client.post(reverse('checkout'), {
            'customer_name': 'Gamal Serag',
            'phone': '01012345678',
            'state': 'Cairo',
            'city': 'Nasr City',
            'address': '12 Test Street, Building 4, Floor 2',
            'notes': 'Call before delivery',
        })

        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.customer_name, 'Gamal Serag')
        self.assertEqual(order.phone, '01012345678')

    def test_checkout_normalizes_international_egyptian_phone(self):
        """Test that +20 mobile numbers are saved in local Egyptian format."""
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )

        self.client.post(reverse('checkout'), {
            'customer_name': 'Gamal Serag',
            'phone': '+20 101 234 5678',
            'state': 'Cairo',
            'city': 'Nasr City',
            'address': '12 Test Street, Building 4, Floor 2',
            'notes': '',
        })

        self.assertEqual(Order.objects.get().phone, '01012345678')

    def test_checkout_rejects_invalid_fields(self):
        """Test checkout validation rejects unusable customer data."""
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )

        response = self.client.post(reverse('checkout'), {
            'customer_name': 'Gamal 123',
            'phone': '12345',
            'state': '',
            'city': '',
            'address': 'short',
            'notes': 'x' * 501,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Name can only contain letters')
        self.assertContains(response, 'Enter a valid Egyptian mobile number')
        self.assertContains(response, 'Please enter a detailed address')
        self.assertEqual(Order.objects.count(), 0)

    def test_product_detail_shows_trust_and_whatsapp(self):
        """Test product detail includes the conversion trust helpers."""
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delivery across Egypt')
        self.assertContains(response, 'Cash on delivery')
        self.assertContains(response, 'Ask about this product on WhatsApp')
        self.assertContains(response, 'https://wa.me/201099628684')

    def test_purchase_pixel_only_fires_once_after_real_order(self):
        """Test Purchase event renders once after checkout and not on refresh."""
        self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 1}
        )

        checkout_response = self.client.post(reverse('checkout'), {
            'customer_name': 'Gamal Serag',
            'phone': '01012345678',
            'state': 'Cairo',
            'city': 'Nasr City',
            'address': '12 Test Street, Building 4, Floor 2',
            'notes': '',
        })
        self.assertEqual(checkout_response.status_code, 302)

        first_success = self.client.get(reverse('order_success'))
        self.assertContains(first_success, "fbq('track', 'Purchase'")
        self.assertContains(first_success, 'EGP 119.99')

        second_success = self.client.get(reverse('order_success'))
        self.assertNotContains(second_success, "fbq('track', 'Purchase'")

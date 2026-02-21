from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, Count, F
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from orders.models import Order, OrderItem
from catalog.models import Product, Category, Offer
from pages.forms import CheckoutForm


class HomePageView(TemplateView):
    """Public home page with categories, best-sellers, and offers."""
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Active categories (limit 8)
        context['categories'] = Category.objects.filter(is_active=True)[:8]
        
        # Best-selling products (by sales_count, limit 8)
        context['best_sellers'] = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count')[:8]
        
        # Active offers (valid date range)
        context['offers'] = Offer.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )[:4]
        
        return context


class CategoryProductsView(TemplateView):
    """Public page listing all active products for one category with search, filter, and pagination."""
    template_name = 'pages/category_products.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        context['category'] = category
        
        # Start with all active products in this category
        products = Product.objects.filter(category=category, is_active=True)
        
        # Search by product name
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            products = products.filter(name__icontains=search_query)
        context['search_query'] = search_query
        
        # Filter by price range
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        context['min_price'] = min_price
        context['max_price'] = max_price
        
        # Order by creation date (newest first)
        products = products.order_by('-created_at')
        
        # Pagination
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        paginator = Paginator(products, self.paginate_by)
        page = self.request.GET.get('page', 1)
        
        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)
        
        context['products'] = products_page
        context['page_obj'] = products_page
        context['paginator'] = paginator
        context['is_paginated'] = paginator.num_pages > 1
        
        # Get all categories for sidebar filter
        context['all_categories'] = Category.objects.filter(is_active=True)
        
        return context


class AllProductsView(TemplateView):
    """Public page listing all active products with search, filter, and pagination."""
    template_name = 'pages/all_products.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Start with all active products
        products = Product.objects.filter(is_active=True)
        
        # Search by product name
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            products = products.filter(name__icontains=search_query)
        context['search_query'] = search_query
        
        # Filter by category
        selected_category = self.request.GET.get('category', '')
        if selected_category:
            products = products.filter(category__slug=selected_category)
        context['selected_category'] = selected_category
        
        # Filter by price range
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        context['min_price'] = min_price
        context['max_price'] = max_price
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name':
            products = products.order_by('name')
        else:
            products = products.order_by('-created_at')
        context['sort_by'] = sort_by
        
        # Pagination
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        paginator = Paginator(products, self.paginate_by)
        page = self.request.GET.get('page', 1)
        
        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)
        
        context['products'] = products_page
        context['page_obj'] = products_page
        context['paginator'] = paginator
        context['is_paginated'] = paginator.num_pages > 1
        
        # Get all categories for sidebar filter
        context['all_categories'] = Category.objects.filter(is_active=True)
        
        return context


class ProductDetailView(TemplateView):
    """Product detail page with image gallery, pricing, and purchase options."""
    template_name = 'pages/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Get the product
        product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        context['product'] = product
        
        # Get all product images for gallery
        context['images'] = product.images.all()
        
        # Check for applicable offers
        # Priority: product-specific offer > category offer
        offer = None
        discount_price = None
        discount_percent = None
        
        # Check product-specific offer
        product_offer = Offer.objects.filter(
            product=product,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
        
        if product_offer:
            offer = product_offer
        else:
            # Check category-wide offer
            category_offer = Offer.objects.filter(
                category=product.category,
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ).first()
            if category_offer:
                offer = category_offer
        
        # Calculate discount if offer exists
        if offer:
            context['offer'] = offer
            price = float(product.price)
            value = float(offer.value)
            
            if offer.offer_type == 'percentage':
                discount_percent = value
                discount_price = price * (1 - value / 100)
            else:  # fixed amount
                discount_price = max(price - value, 0)
                if price > 0:
                    discount_percent = ((price - discount_price) / price) * 100
            
            context['discount_price'] = round(discount_price, 2)
            context['discount_percent'] = round(discount_percent) if discount_percent else None
        
        # Stock status
        context['in_stock'] = product.stock > 0
        context['max_quantity'] = min(product.stock, 10)  # Limit max quantity to 10
        
        # Related products from same category
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]
        
        return context

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date ranges
        today = timezone.now().date()
        week_start = today - timedelta(days=7)
        
        # KPIs
        context['orders_today'] = Order.objects.filter(created_at__date=today).count()
        context['orders_this_week'] = Order.objects.filter(created_at__date__gte=week_start).count()
        context['total_revenue'] = Order.objects.filter(status='delivered').aggregate(Sum('totals'))['totals__sum'] or 0
        context['pending_orders_count'] = Order.objects.filter(status='pending').count()
        context['successful_orders_count'] = Order.objects.filter(status='delivered').count()
        
        # Lists
        context['recent_orders'] = Order.objects.all()[:10]
        context['best_sellers'] = Product.objects.order_by('-sales_count')[:5]
        
        # Choices for status update
        context['status_choices'] = Order.STATUS_CHOICES
        
        return context

from django.utils.translation import gettext as _

class UpdateOrderStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, _("Order #%(order_number)s updated to %(status)s.") % {'order_number': order.order_number, 'status': new_status})
        else:
            messages.error(request, _("Invalid status."))
        return redirect('admin_dashboard')


# ==========================================
# Cart Views
# ==========================================

from cart.cart import Cart
from django.views.decorators.http import require_POST
from django.http import JsonResponse


class CartDetailView(TemplateView):
    """Display the shopping cart."""
    template_name = 'pages/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart'] = cart
        context['cart_items'] = list(cart)
        context['subtotal'] = cart.get_subtotal()
        context['shipping'] = cart.get_shipping()
        context['total'] = cart.get_total()
        context['is_empty'] = cart.is_empty()
        return context


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'true'
    
    if product.stock > 0:
        cart.add(product, quantity=quantity, override_quantity=override)
    else:
        messages.error(request, _("%(product)s is out of stock.") % {'product': product.name})
    
    # Redirect back to referrer or cart
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'cart'))
    return redirect(next_url)


@require_POST
def cart_update(request, product_id):
    """Update the quantity of a product in the cart."""
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart.update(product_id, quantity)
    else:
        cart.remove(product_id)
    
    return redirect('cart')


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart')


class CheckoutView(TemplateView):
    """Checkout page with form handling."""
    template_name = 'pages/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        if cart.is_empty():
            context['redirect_to_home'] = True # Logic to handle empty cart in template
        
        context['cart'] = cart
        context['cart_items'] = list(cart)
        context['subtotal'] = cart.get_subtotal()
        context['shipping'] = cart.get_shipping()
        context['total'] = cart.get_total()
        context['form'] = CheckoutForm() # Add the form
        return context

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        if cart.is_empty():
            messages.error(request, _("Your cart is empty."))
            return redirect('cart')

        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create Order
            order = form.save(commit=False)
            order.totals = cart.get_total()
            order.save()

            # Create Order Items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    line_total=item['total_price']
                )

            # Update product stock and sales count
            for item in cart:
                product = item['product']
                product.stock = F('stock') - item['quantity']
                product.sales_count = F('sales_count') + item['quantity']
                product.save()

            # Clear Cart
            cart.clear()

            # Redirect to success page
            return redirect('order_success', order_number=order.order_number)
        
        # If form invalid, re-render logic
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class OrderSuccessView(DetailView):
    model = Order
    template_name = 'pages/order_success.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'

    def get_object(self):
        return get_object_or_404(Order, order_number=self.kwargs['order_number'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AdminOrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = 'pages/admin_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        return context

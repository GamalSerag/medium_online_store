from django.urls import path
from .views import (
    AdminDashboardView, UpdateOrderStatusView, HomePageView, 
    CategoryProductsView, ProductDetailView, CartDetailView,
    cart_add, cart_update, cart_remove, CheckoutView, OrderSuccessView,
    AdminOrderDetailView, AllProductsView
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/', AllProductsView.as_view(), name='all_products'),
    path('category/<slug:slug>/', CategoryProductsView.as_view(), name='category_products'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Cart URLs
    path('cart/', CartDetailView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    
    # Checkout URL
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-success/', OrderSuccessView.as_view(), name='order_success'),
    
    # Admin URLs
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/order/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-dashboard/order/<int:pk>/update/', UpdateOrderStatusView.as_view(), name='update_order_status'),
]

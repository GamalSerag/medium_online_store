from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Product, ProductImage, Offer


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['name', 'price', 'compare_at_price', 'discount_percentage', 'stock', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer_type', 'value', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'offer_type']
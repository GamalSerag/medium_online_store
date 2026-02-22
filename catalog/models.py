from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Best-seller tracking: denormalized field for read performance
    sales_count = models.PositiveIntegerField(default=0, db_index=True)
    
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        # Calculate price based on discount_percentage
        if self.discount_percentage > 0:
            if self.compare_at_price is None:
                # If no original price set, assign current price to it
                self.compare_at_price = self.price
            
            # Calculate new selling price
            from decimal import Decimal
            discount_factor = Decimal(1) - (Decimal(self.discount_percentage) / Decimal(100))
            self.price = self.compare_at_price * discount_factor
            
        super().save(*args, **kwargs)
    
    @property
    def on_sale(self):
        return self.compare_at_price is not None and self.compare_at_price > self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, help_text='e.g. #FF0000')
    image = models.ImageField(upload_to='products/colors/', blank=True, null=True, help_text='Image for this color variant')
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f"{self.name} ({self.hex_code})"


class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    title = models.CharField(max_length=255)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Optional filtering
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_offers')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_offers')

    def __str__(self):
        return self.title
    
    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

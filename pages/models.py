from django.db import models
from django.utils import timezone


class WebsiteVisitor(models.Model):
    visitor_key = models.CharField(max_length=64, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    is_verified_browser = models.BooleanField(default=False, db_index=True)
    first_seen_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    visit_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_seen_at']
        verbose_name = 'Website visitor'
        verbose_name_plural = 'Website visitors'

    def __str__(self):
        return self.country_name or self.ip_address or self.visitor_key


class PageVisit(models.Model):
    visitor = models.ForeignKey(WebsiteVisitor, related_name='page_visits', on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    full_path = models.CharField(max_length=1000)
    page_title = models.CharField(max_length=160, blank=True)
    referrer = models.URLField(max_length=1000, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    is_verified_browser = models.BooleanField(default=False, db_index=True)
    visited_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['path', '-visited_at']),
            models.Index(fields=['country_code', '-visited_at']),
        ]
        verbose_name = 'Page visit'
        verbose_name_plural = 'Page visits'

    def __str__(self):
        return f'{self.path} - {self.visited_at:%Y-%m-%d %H:%M}'

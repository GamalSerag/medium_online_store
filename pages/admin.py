from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from .analytics import exclude_automated_visits
from .models import PageVisit, WebsiteVisitor


@admin.register(WebsiteVisitor)
class WebsiteVisitorAdmin(admin.ModelAdmin):
    list_display = (
        'visitor_key',
        'country_name',
        'city',
        'ip_address',
        'is_verified_browser',
        'visit_count',
        'first_seen_at',
        'last_seen_at',
    )
    list_filter = ('is_verified_browser', 'country_code', 'country_name')
    search_fields = ('visitor_key', 'ip_address', 'country_name', 'city', 'user_agent')
    readonly_fields = (
        'visitor_key',
        'ip_address',
        'user_agent',
        'country_code',
        'country_name',
        'city',
        'is_verified_browser',
        'first_seen_at',
        'last_seen_at',
        'visit_count',
    )
    date_hierarchy = 'last_seen_at'

    def has_add_permission(self, request):
        return False


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'country_name', 'ip_address', 'is_verified_browser', 'visitor', 'visited_at')
    list_filter = ('is_verified_browser', 'country_code', 'country_name', 'path')
    search_fields = ('path', 'full_path', 'referrer', 'ip_address', 'country_name', 'city', 'user_agent')
    readonly_fields = (
        'visitor',
        'path',
        'full_path',
        'page_title',
        'referrer',
        'user_agent',
        'ip_address',
        'country_code',
        'country_name',
        'city',
        'is_verified_browser',
        'visited_at',
    )
    date_hierarchy = 'visited_at'

    def has_add_permission(self, request):
        return False


def analytics_dashboard(request):
    now = timezone.localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    visits = exclude_automated_visits(PageVisit.objects.select_related('visitor').filter(is_verified_browser=True))
    today_visits = visits.filter(visited_at__gte=today_start)
    seven_days_ago = today_start - timezone.timedelta(days=6)
    human_visitors = exclude_automated_visits(WebsiteVisitor.objects.filter(is_verified_browser=True))

    top_countries = list(
        visits.values('country_code', 'country_name')
        .annotate(visits=Count('id'), visitors=Count('visitor_id', distinct=True))
        .order_by('-visits')[:8]
    )
    max_country_visits = max([item['visits'] for item in top_countries] or [1])
    for item in top_countries:
        item['label'] = item['country_name'] or item['country_code'] or 'Unknown'
        item['percent'] = round((item['visits'] / max_country_visits) * 100)

    top_pages = list(
        visits.values('path')
        .annotate(visits=Count('id'), visitors=Count('visitor_id', distinct=True))
        .order_by('-visits')[:10]
    )
    max_page_visits = max([item['visits'] for item in top_pages] or [1])
    for item in top_pages:
        item['percent'] = round((item['visits'] / max_page_visits) * 100)

    trend_rows = {
        row['day']: row['visits']
        for row in visits.filter(visited_at__gte=seven_days_ago)
        .annotate(day=TruncDate('visited_at'))
        .values('day')
        .annotate(visits=Count('id'))
    }
    trend = []
    for index in range(7):
        day = (seven_days_ago + timezone.timedelta(days=index)).date()
        trend.append({'label': day.strftime('%d %b'), 'visits': trend_rows.get(day, 0)})
    max_trend = max([item['visits'] for item in trend] or [1])
    for item in trend:
        item['height'] = max(8, round((item['visits'] / max_trend) * 100)) if item['visits'] else 8

    context = {
        **admin.site.each_context(request),
        'title': 'Website Analytics',
        'today_visits': today_visits.count(),
        'today_visitors': today_visits.values('visitor_id').distinct().count(),
        'all_time_visits': visits.count(),
        'all_time_visitors': human_visitors.count(),
        'top_countries': top_countries,
        'top_pages': top_pages,
        'trend': trend,
        'recent_visits': visits[:18],
    }
    return render(request, 'admin/pages/analytics/dashboard.html', context)


_admin_get_urls = admin.site.get_urls


def get_analytics_admin_urls():
    return [
        path('analytics/', admin.site.admin_view(analytics_dashboard), name='analytics_dashboard'),
    ] + _admin_get_urls()


admin.site.get_urls = get_analytics_admin_urls
admin.site.index_template = 'admin/pages/analytics/index.html'

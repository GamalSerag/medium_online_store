import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from pages.analytics import ANALYTICS_COOKIE_NAME
from pages.models import PageVisit, WebsiteVisitor

BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
)


class WebsiteAnalyticsTests(TestCase):
    def test_analytics_tracks_country_from_proxy_header(self):
        response = self.client.get(
            reverse('home'),
            HTTP_USER_AGENT=BROWSER_USER_AGENT,
            HTTP_CF_IPCOUNTRY='EG',
            REMOTE_ADDR='41.33.10.20',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PageVisit.objects.count(), 0)
        token = self.client.cookies[ANALYTICS_COOKIE_NAME].value
        response = self.client.post(
            reverse('analytics_track'),
            data=json.dumps({
                'token': token,
                'path': '/products/',
                'full_path': '/products/?sort=newest',
                'title': 'Products',
                'referrer': '',
            }),
            content_type='application/json',
            HTTP_USER_AGENT=BROWSER_USER_AGENT,
            HTTP_CF_IPCOUNTRY='EG',
            REMOTE_ADDR='41.33.10.20',
        )

        self.assertEqual(response.status_code, 200)
        visit = PageVisit.objects.latest('visited_at')
        self.assertEqual(visit.path, '/products/')
        self.assertEqual(visit.full_path, '/products/?sort=newest')
        self.assertEqual(visit.country_code, 'EG')
        self.assertEqual(visit.country_name, 'Egypt')
        self.assertTrue(visit.is_verified_browser)
        self.assertTrue(visit.visitor.is_verified_browser)

    def test_analytics_ignores_googlebot_visits(self):
        response = self.client.get(
            reverse('home'),
            HTTP_USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            REMOTE_ADDR='66.249.66.1',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(ANALYTICS_COOKIE_NAME, self.client.cookies)
        self.assertEqual(PageVisit.objects.count(), 0)
        self.assertEqual(WebsiteVisitor.objects.count(), 0)

    def test_analytics_rejects_client_tracking_without_browser_token(self):
        response = self.client.post(
            reverse('analytics_track'),
            data=json.dumps({'path': '/', 'full_path': '/', 'title': 'Home'}),
            content_type='application/json',
            HTTP_USER_AGENT=BROWSER_USER_AGENT,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PageVisit.objects.count(), 0)
        self.assertEqual(WebsiteVisitor.objects.count(), 0)

    def test_analytics_dashboard_excludes_existing_bot_records(self):
        user = get_user_model().objects.create_superuser(
            username='analytics-admin',
            email='analytics-admin@example.com',
            password='password',
        )
        human = WebsiteVisitor.objects.create(
            visitor_key='human-session',
            user_agent=BROWSER_USER_AGENT,
            country_code='EG',
            country_name='Egypt',
            is_verified_browser=True,
            visit_count=1,
        )
        bot = WebsiteVisitor.objects.create(
            visitor_key='googlebot-session',
            user_agent='Googlebot/2.1',
            country_code='US',
            country_name='United States',
            is_verified_browser=True,
            visit_count=1,
        )
        PageVisit.objects.create(
            visitor=human,
            path='/',
            full_path='/',
            user_agent=BROWSER_USER_AGENT,
            country_code='EG',
            country_name='Egypt',
            is_verified_browser=True,
            visited_at=timezone.now(),
        )
        PageVisit.objects.create(
            visitor=bot,
            path='/',
            full_path='/',
            user_agent='Googlebot/2.1',
            country_code='US',
            country_name='United States',
            is_verified_browser=True,
            visited_at=timezone.now(),
        )
        self.client.force_login(user)

        response = self.client.get(reverse('admin:analytics_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['all_time_visits'], 1)
        self.assertEqual(response.context['all_time_visitors'], 1)
        self.assertEqual(response.context['top_countries'][0]['label'], 'Egypt')

    def test_analytics_dashboard_excludes_unverified_legacy_records(self):
        user = get_user_model().objects.create_superuser(
            username='legacy-analytics-admin',
            email='legacy-analytics-admin@example.com',
            password='password',
        )
        verified = WebsiteVisitor.objects.create(
            visitor_key='verified-session',
            user_agent=BROWSER_USER_AGENT,
            ip_address='41.33.10.20',
            country_code='EG',
            country_name='Egypt',
            is_verified_browser=True,
            visit_count=1,
        )
        unverified = WebsiteVisitor.objects.create(
            visitor_key='legacy-session',
            user_agent=BROWSER_USER_AGENT,
            ip_address='8.8.8.8',
            country_code='US',
            country_name='United States',
            visit_count=1,
        )
        PageVisit.objects.create(
            visitor=verified,
            path='/',
            full_path='/',
            user_agent=BROWSER_USER_AGENT,
            ip_address='41.33.10.20',
            country_code='EG',
            country_name='Egypt',
            is_verified_browser=True,
            visited_at=timezone.now(),
        )
        PageVisit.objects.create(
            visitor=unverified,
            path='/products/',
            full_path='/products/',
            user_agent=BROWSER_USER_AGENT,
            ip_address='8.8.8.8',
            country_code='US',
            country_name='United States',
            visited_at=timezone.now(),
        )
        self.client.force_login(user)

        response = self.client.get(reverse('admin:analytics_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['all_time_visits'], 1)
        self.assertEqual(response.context['all_time_visitors'], 1)
        self.assertEqual(response.context['recent_visits'][0].ip_address, '41.33.10.20')

    @override_settings(ANALYTICS_GEOIP_ENABLED=True)
    def test_analytics_falls_back_to_geoip_lookup(self):
        with patch('pages.middleware.WebsiteAnalyticsMiddleware.lookup_ip_country') as lookup:
            lookup.return_value = {
                'country_code': 'US',
                'country_name': 'United States',
                'city': 'Mountain View',
            }
            self.client.get(
                reverse('home'),
                HTTP_USER_AGENT=BROWSER_USER_AGENT,
                HTTP_X_FORWARDED_FOR='8.8.8.8',
            )
            token = self.client.cookies[ANALYTICS_COOKIE_NAME].value
            response = self.client.post(
                reverse('analytics_track'),
                data=json.dumps({
                    'token': token,
                    'path': '/',
                    'full_path': '/',
                    'title': 'Home',
                }),
                content_type='application/json',
                HTTP_USER_AGENT=BROWSER_USER_AGENT,
                HTTP_X_FORWARDED_FOR='8.8.8.8',
            )

        self.assertEqual(response.status_code, 200)
        lookup.assert_called_once_with('8.8.8.8')
        visitor = WebsiteVisitor.objects.latest('last_seen_at')
        visit = PageVisit.objects.latest('visited_at')
        self.assertEqual(visitor.country_code, 'US')
        self.assertEqual(visit.country_name, 'United States')
        self.assertEqual(visit.city, 'Mountain View')
        self.assertTrue(visit.is_verified_browser)

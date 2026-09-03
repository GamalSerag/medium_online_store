import ipaddress
import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone

from .analytics import (
    ANALYTICS_COOKIE_NAME,
    ANALYTICS_TOKEN_MAX_AGE,
    ANALYTICS_TOKEN_SALT,
    is_bot_user_agent,
    is_browser_user_agent,
)
from .models import PageVisit, WebsiteVisitor

EXCLUDED_PREFIXES = (
    '/admin/',
    '/admin-dashboard/',
    '/analytics/',
    '/static/',
    '/media/',
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
)

COUNTRY_NAMES = {
    'EG': 'Egypt',
    'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates',
    'KW': 'Kuwait',
    'QA': 'Qatar',
    'BH': 'Bahrain',
    'OM': 'Oman',
    'JO': 'Jordan',
    'US': 'United States',
    'GB': 'United Kingdom',
}


class WebsiteAnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if self.should_issue_tracking_token(request, response):
            if not request.session.session_key:
                request.session.save()
            token = signing.TimestampSigner(salt=ANALYTICS_TOKEN_SALT).sign(request.session.session_key)
            response.set_cookie(
                ANALYTICS_COOKIE_NAME,
                token,
                max_age=ANALYTICS_TOKEN_MAX_AGE,
                samesite='Lax',
                secure=request.is_secure(),
            )
        return response

    def record_client_visit(self, request, data):
        if not self.should_track_client_visit(request, data):
            return

        try:
            visitor_key = self.get_visitor_key(request)
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            geo_data = self.get_geo_data(request, ip_address)
            country_code = geo_data.get('country_code', '')
            country_name = geo_data.get('country_name', '')
            city = geo_data.get('city', '')
            now = timezone.now()

            with transaction.atomic():
                visitor, _ = WebsiteVisitor.objects.select_for_update().get_or_create(
                    visitor_key=visitor_key,
                    defaults={
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'country_code': country_code,
                        'country_name': country_name,
                        'city': city[:120],
                        'is_verified_browser': True,
                        'first_seen_at': now,
                        'last_seen_at': now,
                    },
                )
                visitor.ip_address = ip_address or visitor.ip_address
                visitor.user_agent = user_agent or visitor.user_agent
                visitor.country_code = country_code or visitor.country_code
                visitor.country_name = country_name or visitor.country_name
                visitor.city = city[:120] or visitor.city
                visitor.is_verified_browser = True
                visitor.last_seen_at = now
                visitor.visit_count = visitor.visit_count + 1
                visitor.save(update_fields=[
                    'ip_address',
                    'user_agent',
                    'country_code',
                    'country_name',
                    'city',
                    'is_verified_browser',
                    'last_seen_at',
                    'visit_count',
                ])

                PageVisit.objects.create(
                    visitor=visitor,
                    path=(data.get('path') or '/')[:500],
                    full_path=(data.get('full_path') or data.get('path') or '/')[:1000],
                    page_title=(data.get('title') or self.get_page_title(request))[:160],
                    referrer=(data.get('referrer') or '')[:1000],
                    user_agent=user_agent,
                    ip_address=ip_address,
                    country_code=country_code,
                    country_name=country_name,
                    city=city[:120],
                    is_verified_browser=True,
                )
        except Exception:
            return

    def should_issue_tracking_token(self, request, response):
        if request.method != 'GET':
            return False
        if response.status_code >= 400:
            return False
        if any(request.path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return False
        content_type = response.get('Content-Type', '')
        if content_type and 'text/html' not in content_type:
            return False
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not is_browser_user_agent(user_agent):
            return False
        return True

    def should_track_client_visit(self, request, data):
        if request.method != 'POST':
            return False
        if is_bot_user_agent(request.META.get('HTTP_USER_AGENT', '')):
            return False
        path = data.get('path') or ''
        if not path.startswith('/') or any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return False
        token = data.get('token') or request.COOKIES.get(ANALYTICS_COOKIE_NAME)
        cookie_token = request.COOKIES.get(ANALYTICS_COOKIE_NAME)
        if not token or token != cookie_token:
            return False
        try:
            session_key = signing.TimestampSigner(salt=ANALYTICS_TOKEN_SALT).unsign(
                token,
                max_age=ANALYTICS_TOKEN_MAX_AGE,
            )
        except signing.BadSignature:
            return False
        return session_key == request.session.session_key

    def get_visitor_key(self, request):
        if not request.session.session_key:
            request.session.save()
        return request.session.session_key

    def get_client_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def get_geo_data(self, request, ip_address):
        country_code = self.get_country_code_from_headers(request)
        country_name = self.get_country_name_from_headers(request, country_code)
        city = request.META.get('HTTP_CF_IPCITY') or request.META.get('HTTP_X_CITY') or ''
        if country_code or not getattr(settings, 'ANALYTICS_GEOIP_ENABLED', True):
            return {
                'country_code': country_code,
                'country_name': country_name,
                'city': city[:120],
            }

        cached = request.session.get('analytics_geoip')
        if cached and cached.get('ip_address') == ip_address:
            return {
                'country_code': cached.get('country_code', ''),
                'country_name': cached.get('country_name', ''),
                'city': cached.get('city', ''),
            }

        lookup = self.lookup_ip_country(ip_address)
        if lookup:
            request.session['analytics_geoip'] = {
                'ip_address': ip_address,
                **lookup,
            }
            request.session.modified = True
            return lookup

        return {
            'country_code': '',
            'country_name': '',
            'city': '',
        }

    def get_country_code_from_headers(self, request):
        value = (
            request.META.get('HTTP_CF_IPCOUNTRY')
            or request.META.get('HTTP_X_VERCEL_IP_COUNTRY')
            or request.META.get('HTTP_X_COUNTRY_CODE')
            or ''
        )
        value = value.upper().strip()
        if len(value) == 2 and value != 'XX':
            return value
        return ''

    def get_country_name_from_headers(self, request, country_code):
        header_value = request.META.get('HTTP_X_COUNTRY_NAME', '').strip()
        if header_value:
            return header_value[:80]
        return COUNTRY_NAMES.get(country_code, '')

    def lookup_ip_country(self, ip_address):
        if not ip_address:
            return {}
        try:
            parsed_ip = ipaddress.ip_address(ip_address)
        except ValueError:
            return {}
        if parsed_ip.is_private or parsed_ip.is_loopback or parsed_ip.is_reserved or parsed_ip.is_link_local:
            return {}

        endpoint = getattr(settings, 'ANALYTICS_GEOIP_ENDPOINT', '')
        if not endpoint:
            return {}
        timeout = getattr(settings, 'ANALYTICS_GEOIP_TIMEOUT', 0.8)
        url = endpoint.format(ip=ip_address)
        request = Request(url, headers={'User-Agent': 'AlSeragAnalytics/1.0'})
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except (OSError, URLError, TimeoutError, ValueError):
            return {}

        country_code = (
            payload.get('country_code')
            or payload.get('countryCode')
            or payload.get('country')
            or ''
        )
        country_code = str(country_code).upper()[:2]
        if not country_code or country_code == 'XX':
            return {}

        return {
            'country_code': country_code,
            'country_name': str(payload.get('country_name') or payload.get('country') or COUNTRY_NAMES.get(country_code, ''))[:80],
            'city': str(payload.get('city') or '')[:120],
        }

    def get_page_title(self, request):
        match = getattr(request, 'resolver_match', None)
        if match and match.url_name:
            return match.url_name.replace('_', ' ').title()[:160]
        if request.path == '/':
            return 'Home'
        return request.path.strip('/').replace('-', ' ').replace('/', ' / ').title()[:160]

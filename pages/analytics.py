BOT_USER_AGENT_MARKERS = (
    'bot',
    'crawl',
    'crawler',
    'spider',
    'slurp',
    'archiver',
    'googlebot',
    'adsbot-google',
    'apis-google',
    'mediapartners-google',
    'google-inspectiontool',
    'googleother',
    'bingbot',
    'duckduckbot',
    'baiduspider',
    'yandexbot',
    'applebot',
    'petalbot',
    'ahrefsbot',
    'semrushbot',
    'mj12bot',
    'dotbot',
    'serpstatbot',
    'facebookexternalhit',
    'twitterbot',
    'linkedinbot',
    'telegrambot',
    'whatsapp',
    'slackbot',
    'discordbot',
    'pinterestbot',
    'preview',
    'validator',
    'lighthouse',
    'pagespeed',
)

BROWSER_USER_AGENT_MARKERS = (
    'chrome',
    'crios',
    'edg',
    'firefox',
    'fxios',
    'safari',
    'opr',
    'samsungbrowser',
    'mobile',
)

ANALYTICS_COOKIE_NAME = 'alserag_analytics_token'
ANALYTICS_TOKEN_SALT = 'alserag.analytics.browser'
ANALYTICS_TOKEN_MAX_AGE = 60 * 60 * 6


def is_bot_user_agent(user_agent):
    normalized = (user_agent or '').casefold()
    if not normalized:
        return True
    return any(marker in normalized for marker in BOT_USER_AGENT_MARKERS)


def is_browser_user_agent(user_agent):
    normalized = (user_agent or '').casefold()
    if is_bot_user_agent(normalized):
        return False
    return 'mozilla/' in normalized and any(marker in normalized for marker in BROWSER_USER_AGENT_MARKERS)


def exclude_automated_visits(queryset):
    for marker in BOT_USER_AGENT_MARKERS:
        queryset = queryset.exclude(user_agent__icontains=marker)
    return queryset.exclude(user_agent='')

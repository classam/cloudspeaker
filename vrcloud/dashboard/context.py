from django.conf import settings

def globalsettings(request) -> dict:
    """
    This adds a few variables from settings.py to the global context for all templates.
    """
    return {'GOOGLE_ANALYTICS_TOKEN': settings.GOOGLE_ANALYTICS_TOKEN,
            'FAVICON': settings.FAVICON,
            'SITE_TITLE': settings.SITE_TITLE,
            'SITE_META': settings.SITE_META}

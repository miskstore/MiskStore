from django.utils import translation


class ForceDashboardArabicMiddleware:
    """
    Forces Arabic language for all dashboard and chart API endpoints.
    This ensures error messages are always returned in Arabic,
    regardless of the Accept-Language header.
    """
    ARABIC_PATHS = ['/dashboard/', '/charts/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(path in request.path for path in self.ARABIC_PATHS):
            translation.activate('ar')
            request.LANGUAGE_CODE = 'ar'

        response = self.get_response(request)
        return response

class APIAcceptLanguageMiddleware:
    """
    Forces the requested Accept-Language header for /api/ routes.
    This bypasses Django's default LocaleMiddleware cookie preference, 
    ensuring that APIs always translate properly purely based on headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            header = request.META.get('HTTP_ACCEPT_LANGUAGE')
            if header:
                # take first language code (e.g., 'ar', 'ar-eg', 'en')
                lang = header.split(',')[0].strip().split('-')[0].lower()
                if lang in ['ar', 'en']:
                    translation.activate(lang)
                    request.LANGUAGE_CODE = lang

        return self.get_response(request)

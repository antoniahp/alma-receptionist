from django.utils import translation

from domain.rules import language


class ClientLanguageMiddleware:
    """Pasa el idioma de la petición (lo decide LocaleMiddleware con la cabecera Accept-Language)
    a los textos de la recepcionista: así una clienta que usa la web en inglés recibe las respuestas en inglés."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with language.use(translation.get_language()):
            return self.get_response(request)

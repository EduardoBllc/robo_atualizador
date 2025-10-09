class Central:
    def __init__(self):
        pass

    @staticmethod
    def get_url_base():
        from django.conf import settings
        protocolo = 'https:' if settings.CENTRAL_USA_TLS else 'http:'
        return f'{protocolo}//{settings.IP_CENTRAL}:{settings.PORTA_CENTRAL}'
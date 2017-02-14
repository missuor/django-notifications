from django.conf import settings


SETTINGS = getattr(settings, 'NOTIFICATIONS_SETTINGS', {})


FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

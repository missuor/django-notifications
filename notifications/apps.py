from __future__ import unicode_literals
from django.apps import AppConfig
from notifications.signals import notify


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        from notifications.actions import action_handler
        notify.connect(action_handler, dispatch_uid='notifications.models')

# coding=utf-8

from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('__str__', 'level', 'actor', 'verb', 'target', 'public')
    list_editable = ('verb',)
    list_filter = ('timestamp',)
    # raw_id_fields = ('actor_content_type', 'target_content_type', 'action_object_content_type')

admin.site.register(Notification, NotificationAdmin)

# coding=utf-8
from __future__ import unicode_literals

import sys
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timesince import timesince as djtimesince
from django.utils.timezone import now
from django.contrib.contenttypes import fields as generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.conf import settings


class NotificationUserManager(models.query.QuerySet):

    def _unread(self):
        return self.filter(unread=True)

    def unread(self):
        qs = self._unread()
        return qs.select_related('notification', 'user')

    def _read(self):
        return self.filter(unread=False)

    def read(self, include_deleted=False):
        qs = self._read()
        return qs.select_related('notification', 'user')

    def mark_all_as_read(self, user=None):
        qs = self._unread()
        if user:
            qs = qs.filter(user=user)

        return qs.update(unread=False)

    def mark_all_as_unread(self, user=None):
        qs = self._read()
        if user:
            qs = qs.filter(user=user)

        return qs.update(unread=True)


@python_2_unicode_compatible
class NotificationUser(models.Model):
    notification = models.ForeignKey('Notification',
                                     related_name="recipients",
                                     related_query_name="recipient")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="notifications",
                             related_query_name="notification")
    unread = models.BooleanField(default=True)

    objects = NotificationUserManager.as_manager()

    class Meta:
        auto_created = not bool('makemigrations' in sys.argv)
        unique_together = ('notification', 'user')

    def __str__(self):
        ctx = {
            'user': self.user,
            'notification': self.notification,
            'unread': self.unread and 'unread' or 'read'
        }
        return _('(%(unread)s) %(user)s %(notification)s') % ctx

    def to_dict(self):
        data = {
            # 'user': self.user.sketch(),
            'notification': self.notification.to_dict(),
            'unread': self.unread
        }
        return data


class RecipientsMixin(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Notification's (Recipient)Group and (Recipient)User model using the ModelBackend.
    """

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('recipient groups'),
        blank=True,
        help_text=_(
            'The groups this notification belongs to. A user will get all notifications '
            'granted to each of their groups.'
        ),
        related_name="notifications",
        related_query_name="notification"
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('recipient users'),
        blank=True,
        help_text=_('Specific notifications for this user.'),
        # related_name="notifications",
        # related_query_name="notification",
        through='NotificationUser'
    )

    class Meta:
        abstract = True


@python_2_unicode_compatible
class AbstractAction(models.Model):
    """
    See https://github.com/justquick/django-activity-stream/blob/master/actstream/models.py
    """
    actor_content_type = models.ForeignKey(ContentType, related_name='actor',
                                           db_index=True)
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                            related_name='target', db_index=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    target = generic.GenericForeignKey('target_content_type',
                                       'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                                   related_name='action_object', db_index=True)
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    action_object = generic.GenericForeignKey('action_object_content_type',
                                              'action_object_object_id')

    timestamp = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-timestamp')

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return djtimesince(self.timestamp, now).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8')


class Notification(AbstractAction, RecipientsMixin):

    LEVELS = map(lambda i: (i, i), ('success', 'info', 'warning', 'error'))
    level = models.CharField(_('level'), choices=LEVELS, default='info', max_length=20)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this notification should be treated as active. '
            'Unselect this instead of deleting notifications.'
        ),
    )

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')

    def to_dict(self):
        data = {
            'level': self.level,
            'is_active': self.is_active,

            'actor': str(self.actor),
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }

        return data

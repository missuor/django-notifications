# coding=utf-8
# import django_rq
# from django.db.models import signals
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from collections import Iterable
from notifications.models import Notification


def notify_users(instance, users, created=False):
    assert isinstance(instance, Notification)
    if isinstance(users, QuerySet):
        users = users.exclude(pk__in=instance.users.all())
    elif not isinstance(users, Iterable):
        users = [users]
    for u in users:
        instance.users.add(u)


def notify_groups(instance, groups, created=False):
    assert isinstance(instance, Notification)
    if not isinstance(groups, Iterable):
        groups = [groups]

    users = get_user_model().objects.filter(groups__in=instance.groups.all())
    if not created:
        users = users.exclude(pk__in=instance.users.all())
    notify_users(instance, users)

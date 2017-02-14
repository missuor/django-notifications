# coding=utf-8
import django_rq
from django.utils.six import text_type
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from notifications import settings
from notifications import registry
from notifications import models
from notifications import jobs


def action_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon notification signal call.
    """
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')

    # We must store the unstranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, '_proxy____args'):
        verb = verb._proxy____args[0]
    newaction = models.Notification(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=text_type(verb),
        public=bool(kwargs.pop('public', True)),
        description=kwargs.pop('description', None),
        timestamp=kwargs.pop('timestamp', now()),
        level=kwargs.pop('level', 'info')
    )

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if obj is not None:
            registry.check(obj)
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))
    if settings.USE_JSONFIELD and len(kwargs):
        data = kwargs.get('data')
        newaction.data = isinstance(data, dict) and data or kwargs
    newaction.save(force_insert=True)
    for field in ('users', 'groups'):
        objs = kwargs.pop(field, None)
        if objs is not None:
            func = getattr(jobs, 'notify_%s' % field)
            # func(newaction, objs, True)
            django_rq.enqueue(func, newaction, objs, True)
    return newaction

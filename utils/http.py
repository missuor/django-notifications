# coding=utf-8
import json
import datetime
from django import http
from django.db.models.query import QuerySet
from django.utils.timezone import template_localtime
from django.conf import settings


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder subclass that knows how to encode date/time and decimal types."""

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            t = template_localtime(o, settings.USE_TZ)
            r = t.strftime('%Y-%m-%d %H:%M:%S')
            return r

        elif isinstance(o, datetime.date):
            return o.isoformat()

        elif isinstance(o, datetime.time):
            # if is_aware(o):
            #    raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r

        elif hasattr(o, 'to_dict'):
            return o.to_dict()

        elif isinstance(o, QuerySet):
            return list(o)

        else:
            try:
                return super(JSONEncoder, self).default(o)
            except:
                return str(o)


class JSONResponse(http.HttpResponse):

    def __init__(self, data='', status=200):
        self._data = data
        if status == 204:
            content = ''
        else:
            content = json.dumps(data, sort_keys=settings.DEBUG,
                                 cls=JSONEncoder)

        super(JSONResponse, self).__init__(
            status=status,
            content=content,
            content_type='application/json',
        )

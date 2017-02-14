# coding=utf-8
import json
import logging
import traceback
import functools
import django_rq
from django.conf import settings
from django import http
from django.utils import decorators
from utils.http import JSONResponse

DEBUG = settings.DEBUG
logger = logging.getLogger(__name__)


def ajax(authenticated=True, data_required=False, **kwargs):

    def decorator(func, authenticated=authenticated,
                  data_required=data_required):
        @functools.wraps(func, assigned=decorators.available_attrs(func))
        def _wrapped(self, request, *args, **kw):
            if authenticated and not request.user.is_authenticated():
                return JSONResponse({'msg': 'Not logged in', 'action': kwargs.get('action')}, 401)

            request.DATA = None
            if not request.is_ajax() and request.method == "POST":
                request.DATA = request.POST.copy()

            elif request.body:
                try:
                    request.DATA = json.loads(request.body)
                except (TypeError, ValueError) as e:
                    return JSONResponse({'msg': 'malformed JSON request: %s' % e}, 400)
                if DEBUG:
                    print 'request.DATA', request.DATA

            elif not request.is_ajax():
                return JSONResponse({'msg': 'Request must be AJAX'}, 400)

            if data_required:
                if not request.DATA:
                    return JSONResponse({'msg': 'request requires JSON body'}, 400)

            # invoke the wrapped function, handling exceptions sanely
            try:
                data = func(self, request, *args, **kw)
                if isinstance(data, (http.HttpResponse, http.HttpResponseRedirect)):
                    return data
                elif data is None:
                    return JSONResponse('', status=204)

                return JSONResponse(data)

            except Exception as e:
                if settings.DEBUG:
                    traceback.print_exc()
                    raise
                logger.exception('error invoking apiclient')
                return JSONResponse({'msg': str(e)}, 500)

        return _wrapped
    return decorator


def job(func):
    @functools.wraps(func, assigned=decorators.available_attrs(func))
    def _wrapped(*args, **kw):
        queued = kw.pop('queued', False)
        if not queued:
            kw['queued'] = True
            print func, args, kw
            django_rq.enqueue(func, *args, **kw)
    return _wrapped

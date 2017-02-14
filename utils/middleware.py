# coding=utf-8
import json

from django.http.response import HttpResponse
from utils.http import JSONResponse, JSONEncoder


class ResponseMiddleware(object):

    def process_response(self, request, response):
        if isinstance(response, dict):
            data = json.dumps(response, cls=JSONEncoder)
            if 'callback' in request.GET or 'callback' in request.POST:
                data = '%s(%s);' % (request.GET.get('callback', request.POST.get('callback')), data)
                return HttpResponse(data, "text/javascript")
            return JSONResponse(response)

        else:
            return response


class RequestMiddleware(object):

    def process_request(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        if ip:
            ip = ip.split(',')[0]
            ip = ip.strip()
        setattr(request, 'remote_addr', ip)

# coding=utf-8
import json
from django.views.generic import View
from django.http import HttpResponse
from django.http import JsonResponse


class Notifications(View):

    # 获取当前用户状态信息
    def get(self, request, action=None):
        if not request.user.is_authenticated():
            return JsonResponse({'msg': 'Login required.'}, status=401)
        objs = request.user.notifications.unread()
        return {'notifications': objs}

    def put(self, request, action):
        data = json.loads(request.body)
        if action == 'mark-as-read':
            uuids = data.pop('uuids')
            objs = request.user.notifications.unread()
            objs = objs.filter(pk__in=uuids)
            objs.mark_all_as_read()
            return HttpResponse()

        elif action == 'mark-as-unread':
            uuids = data.pop('uuids')
            objs = request.user.notifications.unread()
            objs = objs.filter(pk__in=uuids)
            objs.mark_all_as_unread()
            return HttpResponse()

        elif action == 'mark-all-as-read':
            objs = request.user.notifications.unread()
            objs.mark_all_as_unread()
            return HttpResponse()

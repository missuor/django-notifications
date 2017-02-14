# coding=utf-8
from django.conf.urls import url
from notifications import views
g = {'http_method_names': ('get')}

urlpatterns = [
    url(r'^notifications$', views.Notifications.as_view()),
]

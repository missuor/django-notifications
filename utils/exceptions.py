# coding=utf-8


class AjaxError(Exception):

    def __init__(self, http_status, msg):
        self.http_status = http_status
        super(AjaxError, self).__init__(msg)

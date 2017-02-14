# coding=utf-8
import os
import uuid
import hashlib
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


def md5hex(word):
    """MD5加密算法，返回32位小写16进制符号"""
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()


def md5sum(fn):
    """计算文件的MD5值"""
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)

        # 最后要将游标放回文件开头
        else:
            fh.seek(0)

    m = hashlib.md5()
    if isinstance(fn, basestring) and os.path.exists(fn):
        with open(fn, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)

    # 上传的文件缓存 或 已打开的文件流
    elif fn.__class__.__name__ in ['StringIO', 'StringO'] or isinstance(fn, file):
        for chunk in read_chunks(fn):
            m.update(chunk)

    elif isinstance(fn, (InMemoryUploadedFile, TemporaryUploadedFile)):
        for chunk in fn.chunks():
            m.update(chunk)

    # 未知类型的对象随机生成一个hash
    else:
        return str(uuid.uuid1()).replace('-', '').lower()
    return m.hexdigest()

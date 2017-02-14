# coding=utf-8
import uuid


def random_key(n=6):
    """生成指定长度的随机数, 基于MAC地址、当前时间戳、随机数生成"""
    base = list('abcdefghijklmbopqrstuvwxyzABCDEFGHIJKLMBOPQRSTUVWXYZ0123456789')
    seed = ''.join([str(uuid.uuid1()).replace('-', '').lower()
                    for i in range(n * 4 / 32 + 1)])
    lst = []
    for i in range(n):
        hex_str = seed[i * 4:i * 4 + 4]
        x = int(hex_str, 16)
        lst.append(base[x % 62])
    return ''.join(lst)

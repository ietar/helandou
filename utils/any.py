# -*- coding: utf-8 -*-
__author__ = "ietar"
import copy
import logging
import random

from captcha.image import ImageCaptcha, random_color as rc

from settings import setting1


logger = logging.getLogger('fastapi')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_key_by_value(dic: dict, value):
    values = list(dic.values())
    try:
        index = values.index(value)
    except ValueError:
        return None

    return list(dic.keys()).__getitem__(index)


def ip2int(_ip: str) -> int:
    """
    ipv4
    :param _ip:
    :return:
    """

    parts = _ip.split('.')
    res = 0
    res += int(parts[0]) << 24
    res += int(parts[1]) << 16
    res += int(parts[2]) << 8
    res += int(parts[3])
    return res


def int2ip(_int: int) -> str:
    """
    ipv4
    :param _int:
    :return:
    """
    res = '.'.join([str(_int >> (i * 8) & 0xFF) for i in range(3, -1, -1)])
    return res


def digit_chars(length=6) -> str:
    digits = '1234567890'
    res = ''.join(random.choices(digits, k=length))
    return res


def list_sub(list1: list, list2: list) -> list:
    """
    列表减法 保持顺序
    :param list1: 被减数列表
    :param list2: 减数列表
    :return:
    """
    res = copy.deepcopy(list1)
    for item in list2:
        if item in list1:
            res.remove(item)
    return res


def mk_chars(length=4, exceptions=setting1.get('CHAR_EXCEPTIONS') or 'ioszl10', lower_only=True,
             digit_more=False) -> str:
    """
    生成随机字母数字字符串 a-zA-Z0-9 排除exceptions字符的大小写 数字权重默认较低
    :param length: 生成字符串长度
    :param exceptions: 排除不易辨认的字符
    :param lower_only: 只包含小写字母
    :param digit_more: 数字与字母等量
    :return:
    """
    exceptions = exceptions.lower()
    all_chars = 'abcdefghijklmnopqrstuvwxyz'
    uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '1234567890'

    all_chars += digits
    if not lower_only:
        all_chars += uppers
    if digit_more:
        all_chars += digits

    for char in exceptions:
        all_chars = all_chars.replace(char, '')
        all_chars = all_chars.replace(char.upper(), '')
    res = ''.join(random.choices(all_chars, k=length))
    return res


def make_default_captcha(chars: str, color=(128, 255, None), bg=(0, 128, 50), noise=True, noise_color=None):
    """
    生成
    :param chars: 验证码字符串
    :param color: rgb的begin end opacity
    :param bg: rgb的begin end opacity
    :param noise: 是否带噪音
    :param noise_color: 噪音颜色 形式同color
    :return:
    """
    a = chars
    i = ImageCaptcha()
    b = rc(*bg)
    c = rc(*color)
    img = i.create_captcha_image(chars=a, color=c, background=b)
    if noise:
        img = i.create_noise_curve(image=img, color=noise_color or c)
    return img


def hidden_email(email: str, number=4):
    """隐藏邮箱的用户名部分"""
    return email.split('@', 1)[0][:-number] + '****@' + email.split('@', 1)[1]


if __name__ == '__main__':
    # _ip = ip2int('127.0.0.1')
    # print(_ip, type(_ip))
    # add = int2ip(_ip)
    # print(add, type(add))
    #
    # for test in range(1, 3000):
    #     try:
    #         test_ip = int2ip(test)
    #         test_int = ip2int(test_ip)
    #         if test_int != test:
    #             print(test)
    #     except IndexError as e:
    #         print(f'{e} {test}')
    #         input('continue?:')
    #         continue
    # print(ip2int('127.0.0.1'))
    # print(int2ip(4294967295))

    pass

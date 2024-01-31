#!/usr/bin/python
# coding:utf-8

import enum


class Proxy(enum.Enum):
    GHPROXY = "https://ghproxy.net/"
    MOEYY = "https://github.moeyy.xyz/"
    KKGITHUB = "https://github.com/"


class RimeSchema(enum.Enum):
    RIME_ICE = "https://github.com/iDvel/rime-ice.git"
    """雾凇拼音"""
    RIME_CLOVER_PINYIN = "https://github.com/fkxxyz/rime-cloverpinyin.git"
    """四叶草拼音"""

def splice_proxy(proxy: Proxy, url: str) -> str:
    if proxy in [Proxy.GHPROXY, Proxy.MOEYY]:
        return proxy.value + url
    elif proxy in [Proxy.KKGITHUB]:
        return url.replace("https://github.com/", proxy.value)
    else:
        return url

# coding: utf-8
# created by shijiliang on 2020-03-24

"""从 mooncell 获取数据
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from parser import parse
from utils import csv_to_list_of_dict


def get_basic_info_of_servants(as_raw=False):
    """获取英灵图鉴首页数据, 匹配到的是源码中的单行 csv 文本
    Args:
        as_raw: bool, default False, 返回原文本还是解析后的 List[Dict]
    Raises:
        ValueError: 未在网页源码中匹配到所需数据
    Returns: Union[str, List[Dict]], 匹配到的数据, 根据参数 as_raw 确定返回格式
    """
    url = 'https://fgo.wiki/w/%E8%8B%B1%E7%81%B5%E5%9B%BE%E9%89%B4'
    resp = requests.get(url=url)
    matched = re.findall(r'var raw_str = "(.*?)";', resp.text)
    if len(matched) != 1:
        # 只能匹配到一条
        raise ValueError('未在英灵图鉴网页中匹配到数据')

    # 替换为真正的换行符, 名称中的点号替换为英文, 用于单个英灵的访问
    raw = matched[0].replace('\\n', '\n').replace('・', '·')
    if as_raw:
        return raw
    # 转为 json 的形式
    return csv_to_list_of_dict(raw)


def get_lv_hp_atk(name_cn):
    """根据英灵名获取成长曲线数据
    Args:
        name_cn: str, 英灵中文名, 据此生成 url
    Raises:
        ValueError: 未在网页源码中匹配到成长曲线数据, 无法将匹配到的数据转为 json
    Returns: dict, 匹配到的数据
    """
    url = f"https://fgo.wiki/w/{name_cn}"
    patten = r'"name":"table","values":(.*?)},{"name":"curLv",'
    resp = requests.get(url=url)
    matched = re.findall(patten, resp.text)
    if not (len(matched) == 2 and matched[0] == matched[1]):
        # 代码重复, 确实匹配到两条一样的数据
        raise ValueError(f'未匹配到{name_cn}的成长曲线数据')

    try:
        return json.loads(matched[0])
    except json.JSONEncoder as e:
        raise ValueError(f"无法将匹配到的成长曲线数据转为 json: {e}")


def get_servant(name_cn):
    """根据英灵名获取详情数据
    Args:
        name_cn: str, 英灵中文名, 据此生成 url
    Raises:
        ValueError: 未在网页源码中匹配到成长曲线数据, 无法将匹配到的数据转为 json
    Returns: dict 解析后的字典数据
    """
    url = f"https://fgo.wiki/index.php?title={name_cn}&action=edit"
    resp = requests.get(url=url)
    soup = BeautifulSoup(resp.text, 'lxml')
    # 在编辑源码页面中应当匹配到唯一的 textarea
    tas = soup.find_all('textarea')
    if len(tas) != 1:
        raise ValueError('网页格式有变动, 无法进行解析')

    # 返回解析后的数据
    return parse(tas[0].text)

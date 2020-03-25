# coding: utf-8
# created by shijiliang on 2020-03-24

"""英灵详情解析规则
"""
from functools import partial

# 名称与解析函数的对应
parsers = {}
# 可能包含多项的名称
multi_values = []


def register(func=None, name: str = None, multi=False):
    """将函数注册到 parser, 并确认是否包含多项"""
    if func is None:
        return partial(register, name=name, multi=multi)

    if name in parsers:
        raise ValueError(f'name {name} has already been registered')

    parsers[name] = func
    if multi:
        multi_values.append(name)
    return func


def split(s):
    """对 `{{` 和 `}}` 包围的数据根据 `|` 进行拆分,
    但要忽略中括号和大括号包围的 `|`
    目前还无法处理嵌套和出现 <tabber> 的情况
    """
    rv = []
    flag = True
    last = 0
    for i in range(0, len(s)):
        if s[i] == '|' and flag:
            rv.append(s[last:i])
            last = i + 1
        elif s[i] in '[{':
            flag = False
        elif s[i] in ']}':
            flag = True
    rv.append(s[last:len(s)])
    return rv


@register(name='个人资料')
@register(name='基础数值')
@register(name='宝具', multi=True)
def _parse_kv(s):
    """最普通的 {{name|k1=v1|k2=v2|k3=v3}} 的情况
    若解析出错一般是之前的 split 函数出现了问题
    """
    data = split(s)
    rv = {}
    for d in data[1:]:
        try:
            k, v = d.split('=', 1)
            rv[k] = v
        except ValueError:
            print(f"ERROR: d: {d}; s: {s}")
    return rv


@register(name='持有技能', multi=True)
def _parse_skill(s):
    """持有技能的解析, 项第0为名称, 1到4固定,
    第5项起每11项是名称和数值的对应
    """
    data = split(s)
    rv = {
        'pic': data[1],
        'name_cn': data[2],
        'name_jp': data[3],
        'charge_time': data[4]
    }
    i = 5
    while i < len(data):
        rv[data[i]] = data[i+1: i+10]
        i = i + 11
    return rv


@register(name='职阶技能')
def _parse_class_skill(s):
    """职阶技能的解析, 第0项为名称, 之后每四项一组"""
    data = split(s)
    names = ('note', 'pic', 'name', 'rank')
    rv = []
    tmp = {}
    for i in range(1, len(data)):
        tmp[names[i % 4]] = data[i]
        if i % 4 == 0:
            rv.append(tmp)
            tmp = {}
    return rv


def match_dicts(s):
    """从标记原文中解析出 dict, 相当于括号匹配, 只取最外层的"""
    rv = []
    count = 0
    last = 0
    decline = False
    for i in range(0, len(s)):
        if s[i] == '{':
            count += 1
            decline = False
            if count == 2:
                last = i + 1
        elif s[i] == '}':
            count -= 1
            decline = True
        if count == 0 and decline:
            rv.append(s[last:i-1])
            decline = False
    return rv


def parse(content):
    """匹配文本内容并返回解析后的数据
    Args:
        content: str, textarea 中的 wiki 源码文本
    Returns: dict 解析后的字典数据
    """
    matched = match_dicts(content.replace('\n', ''))
    rv = {x: [] for x in multi_values}
    for item in matched:
        for name, func in parsers.items():
            if item.startswith(name):
                # 根据名称分配解析函数
                value = func(item)
                # 多项的 append, 单项的赋值
                if name in multi_values:
                    rv[name].append(value)
                else:
                    rv[name] = value
    return rv

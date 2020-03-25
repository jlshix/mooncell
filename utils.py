# coding: utf-8
# created by shijiliang on 2020-03-24

"""项目需要的通用工具
"""
import json
from random import uniform
from time import sleep

from pymongo import MongoClient

db = MongoClient(host='localhost', port=27017).get_database('mooncell')
col = db['servants']


def random_sleep(start, end):
    sleep(uniform(start, end))


def to_csv(name, content):
    """将内容写入文本
    Args:
        name: str, 文件名
        content: str, 文件内容, 换行和逗号自带
    """
    with open(name, 'w') as f:
        f.write(content)
    print(f"已生成 {name} 文件")


def to_json(name, dic):
    """将字典数据存为json
    Args:
        name: str, 文件名
        dic: dict, 字典数据
    """
    with open(name, 'w') as f:
        f.write(json.dumps(dic, ensure_ascii=False, indent=2))
    print(f"已生成 {name} 文件")


def csv_to_list_of_dict(content):
    """将 csv 多行文本数据转换为由字典元素组成的列表"""
    lines = content.split('\n')
    headers = lines[0].split(',')
    rv = []
    for line in lines[1:]:
        s = dict(zip(headers, line.split(',')))
        rv.append(s)
    return rv


def drop_and_insert_many(data):
    """清空数据库, 将多项数据插入集合中
    Args:
        data: List[Dict], 由字典元素组成的列表内容
    """
    col.drop()
    col.insert_many(data)


def update_one(name_cn, data):
    """向集合中的单条数据更新字段
    Args:
        name_cn: str, 根据英灵中文名匹配
        data: dict, 需要更新的 key 和 value
    """
    col.update_one(
        filter={'name_cn': name_cn},
        update={'$set': data},
        upsert=True
    )

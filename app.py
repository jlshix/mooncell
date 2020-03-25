# coding: utf-8
# created by shijiliang on 2020-03-24

"""主程序入口
"""

from getter import get_basic_info_of_servants, get_lv_hp_atk, get_servant
from utils import drop_and_insert_many, update_one, random_sleep, to_csv


def main():
    """获取全部信息, 存入 mongodb"""
    servants = get_basic_info_of_servants()
    drop_and_insert_many(servants)
    print('已保存从首页获取的英灵基本信息')

    for s in servants:
        name_cn = s.get('name_cn')
        id_ = s.get('id')
        try:
            growth_curve = get_lv_hp_atk(name_cn)
            update_one(name_cn, data={'growth_curve': growth_curve})
            print(f'已保存 {id_}: {name_cn} 的成长曲线')
        except Exception as e:
            print(f"ERROR {type(e)}: {e}")
        random_sleep(1, 3)

        try:
            details = get_servant(name_cn)
            update_one(name_cn, data=details)
            print(f"已保存 {id_}: {name_cn} 的详细信息")
        except Exception as e:
            print(f"ERROR {type(e)}: {e}")
        random_sleep(1, 3)


def get_basic_csv():
    """获取首页基础信息"""
    servants = get_basic_info_of_servants(as_raw=True)
    to_csv('data/servants.csv', servants)


if __name__ == '__main__':
    # main()
    get_basic_csv()

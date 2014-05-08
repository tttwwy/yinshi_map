#coding=utf-8
from django.db import models
import MySQLdb,sys,re,pickle
import logging
# Create your models here.
from django.db import connection

enum = {"sex":
        {
        "woman":"sex = 'f'",
        "man":"sex = 'm'"
        },

          "kind":
        {
             "all":"category in ('2')".decode("utf-8"),
            "wine":"category in ('名酒','啤酒','烈酒','药酒','酒','酒类','酿酒','预调酒','鸡尾酒')".decode("utf-8"),
             "fruit":"category in ('水果')".decode("utf-8"),
            "drink":"category in ('饮品','果汁','饮料','茶饮料','茶')".decode("utf-8"),
            "tea":"category in ('茶','茶文化')".decode("utf-8"),
             "food":"category in ('小吃')".decode("utf-8"),
        },

        "time":
        {
            "morning":"hour(basic_data.createtime) >= 6 and hour(basic_data.createtime) <= 10",
            "noon":"hour(basic_data.createtime) >= 11 and hour(basic_data.createtime) <= 13",
            "afternoon":"hour(basic_data.createtime) >= 14 and hour(basic_data.createtime) <= 17",
            "evening":"hour(basic_data.createtime) >= 18 or hour(basic_data.createtime) <= 5"
        }

       }
def cal_pmi(kind,sex,time,province):
    cursor = connection.cursor()
    result = []
    logging.info("kind:%s sex:%s time:%s province:%s cal_pmi begin:"%(kind,sex,time,province))
    cache_sql = "select content from cache where province = %s and sex = %s and time = %s and kind = %s"
    logging.info("cache sql:%s begin:"%(cache_sql))
    cursor.execute(cache_sql,(province,sex,time,kind))
    cache_result = cursor.fetchone()
    logging.info("cache sql:%s end:"%(cache_sql))

    if cache_result:
        logging.info("kind:%s sex:%s time:%s province:%s in cache:"%(kind,sex,time,province))
        result = pickle.loads(cache_result[0])
    else:
        logging.info("kind:%s sex:%s time:%s province:%s not in cache:"%(kind,sex,time,province))
        where = ""
        param = []
        kind_param = ""
        if province:
            param.append("province = '%s'"%(province))
        if sex:
            param.append(enum["sex"][sex])
        if time:
            param.append(enum["time"][time])

        if param:
            for index,item in enumerate(param):
                if index == 0:
                    where += "where %s "%(item)
                else:
                    where += " and %s "%(item)

        if kind:
            kind_param = " and " + enum["kind"][kind]

        sql = '''select a.food,food_province_count,food_count,
        food_province_count*(select count(*) from basic_data)/(food_count*(select count(*) from basic_data %s ))
        as result from
        ((select food,province,count(food) as food_province_count from basic_data %s group by food having count(food) > 5)a
        inner join
        (select food,count(food) as food_count from basic_data group by food having count(food) > 50)
        b on a.food = b.food ) order by result desc limit 0,50'''%(where,where)

        sql_yinshi = '''select distinct a.food,food_province_count,food_count,
        food_province_count*(select count(*) from basic_data)/(food_count*(select count(*) from basic_data %s ))
        as result from
        ((select food,province,count(food) as food_province_count from basic_data %s group by food having count(food) > 5)a
        inner join
        (select food,count(food) as food_count from basic_data group by food having count(food) > 50)
        b on a.food = b.food ),yinshi_dict where a.food = yinshi_dict.food %s order by result desc limit 0,50'''%(where,where,kind_param)

        logging.info("sql cal begin:%s"%(sql_yinshi))

        cursor.execute(sql_yinshi)
        result = cursor.fetchall()
        logging.info("sql cal end:%s"%(sql_yinshi))

        binary = MySQLdb.Binary(pickle.dumps(result))
        cache_sql = "insert into cache(province,sex,time,kind,content) values(%s,%s,%s,%s,%s)"
        # print cache_sql
        cursor.execute(cache_sql,(province,sex,time,kind,binary))

    logging.info("kind:%s sex:%s time:%s province:%s cal_pmi end:"%(kind,sex,time,province))

    return result
def get_count(kind,word):
    logging.info("get_content begin:")
    key_search = ""
    if kind == "province":
        key_search = "province"
    if kind == "hour":
        key_search = "hour"

    if kind == "month":
        key_search = "month"


    sql = "select food,count(food) from basic_data where food = %s group by %s"
    logging.info("get_content sql:%s"%(sql))

    cursor = connection.cursor()
    cursor.execute(sql,(word,key_search))
    food_count = cursor.fetchall()



    logging.info("get_content end:")
    list = []
    for line in result:
        temp_line = []
        for item in line:
            temp_line.append(item)
        list.append(temp_line)

    return list


def get_content(sex,time,province,word):
    logging.info("get_content begin:")
    where = ""
    param = []
    if province:
        param.append("province = '%s'"%(province))
    if sex:
        param.append(enum["sex"][sex])
    if time:
        param.append(enum["time"][time])
    if word:
        param.append("food = '%s'"%(word))
    else:
        return []

    if param:
        for index,item in enumerate(param):
            if index == 0:
                where += "where %s "%(item)
            else:
                where += " and %s "%(item)
    sql = "select food,province,city,sex,content from basic_data %s limit 0,100"%(where)
    logging.info("get_content sql:%s"%(sql))

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # for line in result:
    #     for item in line:
    #         print item + " "
    #     print "\n"
    logging.info("get_content end:")
    list = []
    for line in result:
        temp_line = []
        for item in line:
            temp_line.append(item)
        list.append(temp_line)

    return list




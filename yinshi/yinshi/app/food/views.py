#coding=utf-8
from django.template.loader import get_template
from django.template import Context
from django.template import Template
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection
import json
import math
import models
import logging

def index(request):
    logging.info("hello open")
    return render_to_response('base.html')
def base(request):
    logging.info("test open")
    return render_to_response('base.html')

def debug(request):
    logging.info("debug open")
    return render_to_response('debug.html')

def compare(request):
    return render_to_response('compare.html')
def test(request):
    return render_to_response('test.html')


def get_content(request):
    sex = request.GET.get('sex')
    time = request.GET.get('time')
    province = request.GET.get('province')
    word = request.GET.get('word')

    result = models.get_content(sex,time,province,word)
    for index,line in enumerate(result):
        if line[3] and line[3] == "f":
            result[index][3] = "女"
        if line[3] and line[3] == "m":
            result[index][3] = "男"
        result[index][4] = line[4].replace(line[0],"<span style='color:red'>" + line[0] + "</span>")
    t = get_template('content.html')
    context = Context({'content':result})
    html = t.render(context)
    return HttpResponse(html)


def wordcloud(request):
    sex = request.GET.get('sex')
    time = request.GET.get('time')
    province = request.GET.get('province')
    kind = request.GET.get('kind')
    result = models.cal_pmi(kind,sex,time,province)

    logging.info("request info sex:%s time:%s province:%s kind:%s "%(sex,time,province,kind))


    list = {"weight":[],"color":{}}

    for index,line in enumerate(result):
        if index == 30:
            break
        list["weight"].append([line[0],35-index])
        list["color"][line[0]] = int(line[2])
        logging.info("result:%s"%(line[0]))


    sort_color = sorted(list["color"].items(),key=lambda a:a[0],reverse=False)
    for index,(key,value) in enumerate(sort_color):
        list["color"][key] = get_color(0,len(sort_color)-1,index)

    logging.info("wordcloud done!")
    return HttpResponse(json.dumps(list))

def get_color(min,max,weight):
    colorlist = ['239ccc','3c9e01','b4d701','fc2c02','e10001']
    color = ""
    weight = ( weight - min ) * (len(colorlist) - 1) * 1.0 /( max - min )
    left = colorlist[int(weight)]

    right = colorlist[int(math.ceil(weight))]
    for i in range(0,3):
        item =  "%02X"%(int( (int(left[i*2:i*2+2],16) + int(right[i*2:i*2+2],16) ) * 0.5 ))
        # print item
        color += item
    return color




def gen_cache(request):
    print "begin to gen cache"
    logging.info("begin to gen cache")

    count = 0
    kinds = ["fruit","food","drink","wine","tea","all"]
    sexs = ["man","woman",""]
    times = ["morning","noon","afternoon","evening",""]
    provinces = ["北京".decode('utf-8'),
                    "浙江".decode('utf-8'),
                    "天津".decode('utf-8'),
                    "安徽".decode('utf-8'),
                    "上海".decode('utf-8'),
                    "福建".decode('utf-8'),
                    "重庆".decode('utf-8'),
                    "江西".decode('utf-8'),
                    "山东".decode('utf-8'),
                    "河南".decode('utf-8'),
                    "湖北".decode('utf-8'),
                    "湖南".decode('utf-8'),
                    "广东".decode('utf-8'),
                    "海南".decode('utf-8'),
                    "山西".decode('utf-8'),
                    "青海".decode('utf-8'),
                    "江苏".decode('utf-8'),
                    "辽宁".decode('utf-8'),
                    "吉林".decode('utf-8'),
                    "台湾".decode('utf-8'),
                    "河北".decode('utf-8'),
                    "贵州".decode('utf-8'),
                    "四川".decode('utf-8'),
                    "云南".decode('utf-8'),
                    "陕西".decode('utf-8'),
                    "甘肃".decode('utf-8'),
                    "黑龙江".decode('utf-8'),
                    "香港".decode('utf-8'),
                    "澳门".decode('utf-8'),
                    "广西".decode('utf-8'),
                    "宁夏".decode('utf-8'),
                    "新疆".decode('utf-8'),
                    "内蒙古".decode('utf-8'),
                    "西藏".decode('utf-8'),
                    ""]
    for province in provinces:
        for sex in sexs:
            for time in times:
                for kind in kinds:
                    result = models.cal_pmi(kind,sex,time,province)
                    print "add cache sex:%s time:%s province:%s kind:%s "%(sex,time,province,kind)
                    logging.info("add cache sex:%s time:%s province:%s kind:%s "%(sex,time,province,kind))
    logging.info("gen cache end")
    print ("%s:gen cache end")


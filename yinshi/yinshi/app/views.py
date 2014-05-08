from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection
import datetime

def hello(request):
    cursor = connection.cursor()
    return render_to_response('index.html')

def compare(request):
    cursor = connection.cursor()
    return render_to_response('compare.html')
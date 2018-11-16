from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
import json
import time
import datetime
from app01.models import *
# Create your views here.


def show_time(req):
    t = time.ctime()
    return render(req,"index.html",{"t":t})

def login(req):
    if req.method=="POST":
        if 1:
            # return redirect("/yuan_back/")
            name="yuanhao"

            return render(req,"back.html",locals())

    return render(req,"login.html",locals())

def test(req):

    return render(req,"back.html",locals())

def delete(req):
    name = "success"
    book = Book(title="abook")
    book.save()
    return render(req,"back.html",locals())

def add(req):
    name = "success"
    print("test")
    book_obj = Book.objects.get(id=1)
    author_obj = Author.objects.all()
    book_obj.author.add(*author_obj)
    return render(req,"back.html",locals())


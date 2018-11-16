from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
import json
import time
import datetime
from app01.models import *
# Create your views here.


def index(req):
    if not req.session["is_login"]:
        if req.method == "POST":
            userID = req.POST.get("user_id")
            pwd = req.POST.get("user_pwd")
            if isinstance(pwd,int):
                if pwd>10000:
                    db_pwd = user_info.objects.filter(phone=userID).values("pwd")[0].get("pwd")
                else:
                    db_pwd = user_info.objects.filter(id=userID).values("pwd")[0].get("pwd")
            else:
                db_pwd = user_info.objects.filter(email=userID).values("pwd")[0].get("pwd")
            if db_pwd == pwd:
                req.session["is_login"] = True
                req.session["userID"] = userID
                return HttpResponse(req,"success")
        return render(req,"index.html")
    else:
        return redirect("/main/")

def main(request):
    if request.session["is_login"]:
        username = user_info.objects.filter(id = request.session["userID"]).values("userName")[0]["userName"]
        return render(request,"main.html",locals())
    else:
        return redirect("/index/")


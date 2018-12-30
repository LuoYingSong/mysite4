from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Avg, Min, Sum, Max
import json
import time
import datetime
from app01.models import *
from django.db.models import Q
import shutil


def index(req):
    if not req.session.get("is_login", None):
        try:
            if req.method == "POST":
                user_id = req.POST.get("user_id")
                pwd = req.POST.get("user_pwd")
                if user_id.isdigit():
                    if int(user_id) > 1000000:
                        db_data = user_info.objects.filter(phone=user_id).values("pwd", "id")[0]
                        db_pwd = db_data.get("pwd")
                        user_id = db_data.get("id")
                    else:
                        db_pwd = user_info.objects.filter(id=user_id).values("pwd")[0].get("pwd")
                else:
                    db_data = user_info.objects.filter(email=user_id).values("pwd")[0]
                    db_pwd = db_data.get("pwd")
                    user_id = db_data.get("id")
                if db_pwd == pwd:
                    req.session["is_login"] = True
                    req.session["user_id"] = user_id
                    return redirect("/main/")
                else:
                    return render(req, "index.html")
            return render(req, "index.html")
        except:
            return HttpResponse("输入错误")
    else:
        return redirect("/main/")


def main(request):
    if request.session.get("is_login", None):
        id = request.session["user_id"][0]
        friend_list = user_info.objects.filter(id=id).values_list("friendsID")[0][0].split(',')
        print(friend_list[0])
        if friend_list[0]:
            friend_list = list(map(lambda x: int(x), friend_list))
        else:
            friend_list = []
        friend_info_list = []
        for each_friend_id in friend_list:
            each_friend_name = user_info.objects.get(id=each_friend_id).userName
            try:
                latest_msg_obj = talk_info.objects.filter(
                    Q(userID=id) & Q(friendID=each_friend_id) | Q(userID=each_friend_id) & Q(friendID=id)).latest(
                    "createTime")
                msg_time = latest_msg_obj.createTime
                detail = latest_msg_obj.talkInfo
                friend_info_list.append(
                    {"time": time.mktime(msg_time.timetuple()), "detail": detail, "talk_name": each_friend_name,
                     "id": each_friend_id})
            except talk_info.DoesNotExist:
                friend_info_list.append(
                    {"time": 9999999999, "detail": "", "talk_name": each_friend_name, "id": each_friend_id})
        friend_info_list.sort(key=lambda x: x["time"])
        friend_info_list.reverse()
        get_user_info = user_info.objects.filter(id=id).values()[0]
        if friend_info_list:
            get_friendid = friend_info_list[0]['id']
            username = user_info.objects.filter(id=id).values_list("userName")[0][0]
        user_id = id
        return render(request, "main.html", locals())
    else:
        return redirect("/index/")


def get_talk(req):
    user_id = req.POST.get("userID")
    friend_id = req.POST.get("friendID")
    # unread_people = json.loads(user_info.objects.filter(id=user_id).values_list("unread_msg")[0])
    # if unread_people:
    #     map(lambda x: int(x), unread_people)
    # if int(friend_id) in unread_people:
    #     unread_people.remove(int(friend_id))
    # user_info.objects.filter(id=user_id).update(unread_people=json.dumps(unread_people))
    get_talk_info = list(talk_info.objects.filter(
        Q(userID=user_id) & Q(friendID=friend_id) | Q(userID=friend_id) & Q(friendID=user_id)).values("talkInfo",
                                                                                                      "userID",
                                                                                                      "msgType",
                                                                                                      "createTime",
                                                                                                      "friendID__userName"))
    for each_talk in get_talk_info:
        each_talk["createTime"] = time.mktime(each_talk["createTime"].timetuple())
    get_talk_info.sort(key=lambda x: x["createTime"])
    return HttpResponse(json.dumps(get_talk_info))


def iforget(req):
    if req.method == "POST":
        try:
            find_id = req.POST.get("old_id")
            old_phone = req.POST.get("old_phone")
            old_email = req.POST.get("old_email")
            new_pwd = req.POST.get("new_pwd")
            get_user_info = user_info.objects.filter(id=int(find_id)).values("phone", "email", "pwd")[0]
            phone = get_user_info.get("phone")
            email = get_user_info.get("email")
            if old_email == email and phone == old_phone:
                user_info.objects.filter(id=int(find_id)).update(pwd=new_pwd)
                return HttpResponse("succeess")
            else:
                return HttpResponse("fail")
        except:
            return HttpResponse("fail")
    else:
        return render(req, "iforget.html")


def register(req):
    if req.method == "POST":
        try:
            user_name = req.POST.get("name")
            email = req.POST.get("email")
            phone = req.POST.get("phone")
            pwd = req.POST.get("pwd")
            get_user_info = user_info.objects.filter(Q(email=email) | Q(phone=phone))
            if len(get_user_info.values_list("id")):
                info = "冲突的邮箱和电话"
                info_type = "warning"
                return render(req,'reason_info.html',locals())
            else:
                user_info.objects.create(userName=user_name, email=email, pwd=pwd, phone=phone, info="null",
                                         saying="null")
                id = user_info.objects.filter(email=email).values_list("id")[0]
                req.session["user_id"] = id
                req.session["is_login"] = True
                if req.FILES:
                    if req.FILES['img'].name.endswith(".png"):
                        with open('./static/img/user_info_picture/'+str(id[0])+".png", "wb") as f:
                            for line in req.FILES['img'].chunks():
                                f.write(line)
                info = "注册成功 你的登入账号{}".format(id)
                info_type = "success"
                return render(req,"reason_info.html",locals())
        except KeyError:
            info = "错误的输入"
            info_type = "warning"
            return render(req,'reason_info.html',locals())
    return render(req, "register.html")


def send_msg(req):
    if not req.FILES:
        rec_user_name = req.POST.get("msg_to")
        rec_id = user_info.objects.filter(userName=rec_user_name).values_list("id")[0][0]
        send_id = req.POST.get("msg_from")[0]
        msg = req.POST.get("msg_info")
        msg_type = req.POST.get("msg_type")[0]
        if req.POST["msg_type"] == '1':
            talk_info.objects.create(userID=rec_id, friendID_id=send_id, talkInfo=msg, msgType=msg_type,
                                     createTime=datetime.datetime.now())
        else:
            file_name = req.POST["file"]
            if file_name.endswith(".png"):
                msg_type = 2
            else:
                while True:
                    try:
                        shutil.move("./static/img/talk_img/" + file_name, "./static/img/send_file/" + file_name)
                        break
                    except FileNotFoundError:
                        continue
                msg_type = 3
            talk_info.objects.create(userID=rec_id, friendID_id=send_id, talkInfo=file_name, msgType=msg_type,
                                     createTime=datetime.datetime.now())
        return HttpResponse("success")
    else:
        file_name = req.FILES["files"].name
        with open("./static/img/talk_img/" + file_name, "wb")as f:
            for line in req.FILES.get("files").chunks():
                f.write(line)
        return HttpResponse("success")


def unlogin(req):
    req.session["is_login"] = False
    return redirect("/index/")


def user_detail(req):
    user_id = req.GET["user_id"]
    if req.session["user_id"] != user_id:
        return HttpResponse("我靠,你在想什么呢小老弟")
    if_me = True
    user_show_info_get = user_info.objects.filter(id=user_id).values("id", "phone", "email", "userName", "saying")[0]
    user_show_info = {
        "账号": user_show_info_get["id"],
        "电话": user_show_info_get["phone"],
        "邮箱": user_show_info_get["email"],
        "昵称": user_show_info_get["userName"],
        "签名": user_show_info_get["saying"]
    }
    return render(req, "user_detail.html", locals())


def change_info(req):
    if req.method == "POST":
        user_id = req.session["user_id"]
        new_phone = req.POST["电话"]
        new_email = req.POST["邮箱"]
        new_name = req.POST["昵称"]
        new_saying = req.POST["签名"]
        user_info.objects.filter(id=user_id).update(phone=new_phone, email=new_email, userName=new_name,
                                                    saying=new_saying)
        img = req.FILES.get("img", None)
        if not img:
            pass
        else:
            with open("./static/img/user_info_picture/" + str(user_id) + ".png", "wb") as f:
                for line in img.chunks():
                    f.write(line)
        return redirect("/user_detail?user_id=" + str(user_id))
    else:
        try:
            user_id = req.GET["user_id"]
            if user_id != req.session["user_id"] and not req.session["is_login"]:
                return HttpResponse("我靠，你又在想什么？")
            else:
                user_show_info_get = \
                    user_info.objects.filter(id=user_id).values("id", "phone", "email", "userName", "saying", "info")[0]
                user_show_info = {
                    "电话": user_show_info_get["phone"],
                    "邮箱": user_show_info_get["email"],
                    "昵称": user_show_info_get["userName"],
                    "签名": user_show_info_get["saying"]
                }
                img_path = user_show_info_get["info"]
                return render(req, "change_info.html", locals())
        except KeyError:
            return HttpResponse("error")


def update_friend(req):
    user_id = req.POST["id"]
    talking_user = int(req.POST["talking_id"])
    change_flag = False
    login_time = user_info.objects.filter(id=user_id).values_list("login_time")[0][0]
    friend_info_list = []
    friend_list = user_info.objects.filter(id=user_id).values_list("friendsID")[0][0].split(",")
    change_talk_content_flag = False
    unread_penple = user_info.objects.filter(id=user_id).values_list("unread_msg")[0]
    # unread_penple = json.loads(unread_penple)
    for each_friend_id in friend_list:
        each_friend_id = int(each_friend_id)
        each_friend_name = user_info.objects.get(id=each_friend_id).userName
        try:
            new_info = False
            latest_msg_obj = talk_info.objects.filter(
                Q(userID=user_id) & Q(friendID=each_friend_id) | Q(userID=each_friend_id) & Q(friendID=user_id)).latest(
                "createTime")
            msg_time = latest_msg_obj.createTime
            if msg_time + datetime.timedelta(hours=8) > login_time:
                new_info = True
                change_flag = True
                # if talking_user not in unread_penple:
                # unread_penple.append(unread_penple)
                if each_friend_id == talking_user:
                    change_talk_content_flag = True
            detail = latest_msg_obj.talkInfo
            if talking_user in unread_penple:
                new_info = True
            friend_info_list.append(
                {"time": time.mktime(msg_time.timetuple()), "detail": detail, "talk_name": each_friend_name,
                 "id": each_friend_id, "isNew": new_info})
        except talk_info.DoesNotExist:
            friend_info_list.append(
                {"time": 9999999999, "detail": "", "talk_name": each_friend_name, "id": each_friend_id, "isNew": False})
    friend_info_list.sort(key=lambda x: x["time"])
    friend_info_list.reverse()
    friend_info_list.insert(0, change_talk_content_flag)
    user_info.objects.filter(id=user_id).update(login_time=datetime.datetime.now())
    if change_flag:
        return HttpResponse(json.dumps(friend_info_list))
    else:
        return HttpResponse("OK")

def find_friend(req):
    user_id = req.POST["id"]
    user_show_info_get = user_info.objects.filter(id=user_id).values("id", "phone", "email", "userName", "saying")[0]
    user_show_info = {
        "账号": user_show_info_get["id"],
        "电话": user_show_info_get["phone"],
        "邮箱": user_show_info_get["email"],
        "昵称": user_show_info_get["userName"],
        "签名": user_show_info_get["saying"]
    }
    return render(req,"add_friend.html",locals())

def add_friend(req):
    user_id = req.session["user_id"]
    add_friend_id = req.POST["add_id"]
    friend_id = user_info.objects.get(id=user_id).friendsID
    if int(user_id) == int(add_friend_id):
        return HttpResponse("请勿添加自己")
    if str(add_friend_id) in friend_id:
        return HttpResponse("已经在好友列表")
    obj = user_info.objects.get(id=user_id)
    if obj.friendsID == "":
        obj.friendsID = str(add_friend_id)
    else:
        obj.friendsID = friend_id + ',' + str(add_friend_id)
    obj.save()
    return HttpResponse("添加成功")

from django.db import models

# Create your models here.

class user_info(models.Model):
    pwd = models.CharField(max_length=32)
    phone = models.CharField(max_length=11)
    email = models.CharField(max_length=32)
    userName = models.CharField(max_length=32)
    saying = models.CharField(max_length=52)
    info = models.CharField(max_length=2048,default=None)
    friendsID = models.TextField()

class talk_info(models.Model):
    userID = models.IntegerField()
    friendID = models.ForeignKey(user_info,on_delete=models.SET_NULL,blank=True, null=True)#逗号分隔的所有朋友信息
    talkInfo = models.TextField(null=True)
    msgType = models.IntegerField(default=1)#消息类型 留作日后修改的空间
    createTime = models.DateTimeField()



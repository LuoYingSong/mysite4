from django.db import models

# Create your models here.

class Book(models.Model):
    # 定义一个自增的id主键
    id = models.AutoField(primary_key=True)
    # 定义一个最大长度为32的varchar字段
    title = models.CharField(max_length=32)
    publish = models.ForeignKey("publish" ,on_delete=models.CASCADE,default=1)
    author = models.ManyToManyField("Author",default=1)
    def __str__(self):
        return self.title

class publish(models.Model):
    name = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    # book = models.ManyToManyField(Book)
    def __str__(self):
        return self.name
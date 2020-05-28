from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# 自定义用户模型类

# 追加mobile字段：字符串类型，最长11位，唯一不重复
class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


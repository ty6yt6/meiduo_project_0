from django.db import models
from django.contrib.auth.models import AbstractUser
from meiduo_mall.utils.models import BaseModel
# Create your models here.
# 自定义用户模型类

# 追加mobile字段：字符串类型，最长11位，唯一不重复
# 追加email_active字段：布尔类型，默认0
class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")
    # 邮箱激活状态
    email_active = models.BooleanField(default=False,verbose_name="邮箱状态")

    # 补充默认地址字段:允许为空，有些用户不指定默认地址
    # on_delete是Django2.x和新版中必备的选项
    default_address = models.ForeignKey("Address",related_name="users",null=True,on_delete=models.SET_NULL,verbose_name="默认地址")


    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    # 用户地址
    # 用户和地址是一对多的关联关系
        # 自定义一查多的关联字段：related_name="addresses"
        # 查询用户关联地址（一查多）：用户模型对象.addresses
        # 查询地址属于的用户（多查一）：地址模型对象.user

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')

    province = models.ForeignKey('areas.Area', # 像这种直接点出来的字符串，Django会在areas中去找Area，省去了导包环节
                                 on_delete=models.PROTECT,
                                 related_name='province',
                                 verbose_name='省')

    city = models.ForeignKey('areas.Area',
                             on_delete=models.PROTECT,
                             related_name='city',
                             verbose_name='市')

    district = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='district',
                                 verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,
                           null=True,
                           blank=True,
                           default='',
                           verbose_name='固定电话')

    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')

    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        # orderting：指定默认的排序规则，如果指定了，那么凡是得到的查询集默认都是按照该规则排好顺序
        # “-update_time”:表示默认的排序规则为按照修改时间倒序，即最近一次新建或修改的地址排列在最前面
        ordering = ['-update_time']
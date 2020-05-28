from django.shortcuts import render
from django.views import View
# 这里users.models 导入User，是从apps开始的，如果把目录写全，则Django不支持，所以只能这样写。
# 这样写pycharm又不支持，所以要把apps这个文件夹添加到导包路径中，右键 + Mark directory as + sources root
from apps.users.models import User
from django import http
# 日志输出器导入
import logging
# Create your views here.

# 日志输出器
logger = logging.getLogger("django")

class UsernameCountView(View):
    # 判断用户名是否重复注册

    # GET http://www.beauty.site:8000/usernames/xxxx/count/
    def get(self,request,username):
        # 1.查询username在数据库中的个数
        try:
            # 模型类.objects.fileter().count()
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                "code":400,
                "errmsg":"访问数据库失败"
            })
        # 2.返回结果(json) --> code和errmsg和count
        return http.JsonResponse({
            "code":0,
            "errmsg":"ok",
            "count":count,
        })
        # return render(request, "front_end_pc/index.html", context)


# 手机号重复注册
class MobileCountView(View):
    def get(self,request,mobile):
        # 1.查询mobile在mysql中的个数
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            return JsonResponse({
                "code":400,
                "errmsg":"查询数据库出错"
            })
        # 2.返回结果（json）
        return JsonResponse({
            "code":0,
            "errmsg":"ok",
            "count":count,
        })
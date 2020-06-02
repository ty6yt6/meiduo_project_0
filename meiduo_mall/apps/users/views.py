from django.shortcuts import render
from django.views import View
# 这里users.models 导入User，是从apps开始的，如果把目录写全，则Django不支持，所以只能这样写。
# 这样写pycharm又不支持，所以要把apps这个文件夹添加到导包路径中，右键 + Mark directory as + sources root
from apps.users.models import User
from django import http
# 日志输出器导入
import logging,json,re
from django.contrib.auth import login
# Create your views here.

# 日志输出器
logger = logging.getLogger("django")

class RegisterView(View):
    # 用户注册
    # POST http://www.beauty.site:8000/register
    def post(self,request):
        # 实现注册逻辑
        # 一、接收参数：请求体中的JSON数据 request.body 得到原始json数据
        # 1.从请求体中获取原始json数据
        json_org = request.body
        # 2.将bytes类型的json数据，转换成json字符串
        json_str = json_org.decode()
        # 3.将json字符串转成python的标准字典
        json_dict = json.loads(json_str)
        # ↑或者3步合1步
        # json_dict = json.loads(request.body.decode())

        # 提取参数
        username = json_dict.get("username")
        password = json_dict.get("password")
        password2 = json_dict.get("password2")
        mobile = json_dict.get("mobile")
        allow = json_dict.get("allow")

        # 校验参数
        # 1.判断是否缺少必传参数
        # all([]):判断某些数据中是否有空的数据,里面传列表数据
        # 只要列表中元素有任意一个为空，则返回False。只有所有的元素不为空，就返回True
        if not all([username,password,password2,mobile,allow]):
            # 如果缺少了必传参数，就返回400的状态码和错误信息，终止逻辑
            return http.JsonResponse({"code":400,"errmsg":"缺少必传的参数"})

        # 2.判断用户名是否满足项目的格式要求
        if not re.match(r"^[a-zA-z0-9_-]{6,20}$",username):
            # 如果用户名不满足格式要求，返回错误信息，立马终止逻辑
            return http.JsonResponse({"code":400,"errmsg":"参数username有误"})
        # 3.判断密码是否满足项目的格式要求
        if not re.match(r"^[a-zA-Z0-9_-]{6,20}$",password):
            # 如果密码不满足格式要求，返回错误信息，终止逻辑
            return http.JsonResponse({"code":400,"errmsg":"参数password有误"})
        # 4.判断用户两次输入的密码是否一致
        if password != password2:
            return http.JsonResponse({"code":400,"errmsg":"参数password2有误"})
        # 5.判断手机号是否满足项目的格式要求
        if not re.match(r"^1[3-9]\d{9}$",mobile):
            return http.JsonResponse({"code":400,"errmsg":"参数mobile有误"})
        # 6.判断是否勾选协议
        if allow != True:
            return http.JsonResponse({"code": 400, "errmsg": "参数allow有误"})

        # 实现核心逻辑：保存注册数据到用户数据表
        # 由于美多商城的用户模块完全依赖于Django自带的用户模型类
        # 所以用户相关的一切操作都需要调用Django自带的用户模型类提供的方法和属性
        # 其中就包括了用户的注册数据，Django自带的用户模型类提供了create_user()专门保存用户的注册数据
        try:
            user = User.objects.create_user(username=username,password=password,mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"code": 400, "errmsg": "注册失败"})

        # 实现状态保持：美多商城的需求是注册成功即登录成功
        # 我们记住当前的用户登录状态时，不用cookie机制，用session机制
        # login()方法是Django提供的用于实现登录、注册状态保持
        # login(“请求对象”，“注册后活着登录认证后的用户”)
        login(request,user)

        # 响应结果：如果注册成功，前端会把用户引导到首页
        return http.JsonResponse({"code":0,"errmsg":"注册成功"})



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
            return http.JsonResponse({
                "code":400,
                "errmsg":"查询数据库出错"
            })
        # 2.返回结果（json）
        return http.JsonResponse({
            "code":0,
            "errmsg":"ok",
            "count":count,
        })
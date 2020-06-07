from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
from apps.oauth.utils import generate_access_token_openid,check_access_token_openid
import json,re
from django_redis import get_redis_connection
from apps.users.models import User
# Create your views here.
class QQURLView(View):
    # QQ登录扫码链接
    # GET /qq/authorization/
    def get(self,request):
        # 提供QQ登录扫码链接
        # 接受next参数
        next = request.GET.get("next","/")
        # 创建OAuthQQ对象
        oauth = OAuthQQ(# 虽说是[settings.]但是东西是放在dev中的，所有配置文件都可以用settings.出来
                        client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        # 调用提供QQ登录扫码链接的接口函数
        login_url = oauth.get_qq_url()

        # 响应结果
        return http.JsonResponse({"code":0,"errmsg":"OK","login_url":login_url})

class QQUserView(View):
    # 处理授权后的回调
    # GET /oauth_callback/

    def get(self,request):
        # 处理授权后的回调逻辑
        code = request.GET.get("code")
        if not code:
            return http.JsonResponse({"code":400,"errmsg":"缺少code"})
        # 创建SDK对象
        oauth = OAuthQQ(  # 虽说是[settings.]但是东西是放在dev中的，所有配置文件都可以用settings.出来
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            )#因为state在回调时原样带回，所以不用再写一遍
        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)
            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return http.JsonResponse({"code":400,"errmsg":"OAuth2.0认证失败"})

        # 使用openid去判断当前的QQ用户是否已经绑定过美多商城的用户
        # （美多商城自己的需求，和OAuth2.0无关，以上已经结束OAuth2.0认证）
        try:
            oauth_model = OAuthQQUser.objects.get(openid=openid)  # 对应的是模型类对象OAuthQQUser，对应的是openid查询出来的一条记录
        except OAuthQQUser.DoesNotExist: # 任何继承自model的模型类GET都可以调DoesNotExist
            # openid未绑定美多商城的用户：将用户引导到绑定用户的页面
            # 为了简单处理，我们将openid还给用户自己保存，将来在绑定用户时，前端再传给后端
            # openid是QQ最隐私的信息之一，不能明文传输或保存，需要加密
            access_token_openid = generate_access_token_openid(openid)

            return http.JsonResponse({"code":300,"errmsg":"用户未绑定","access_token":access_token_openid})
            # 前端写的这种未绑定的情况是300;前端也把最后一项openid名字设定好了，叫access_token
            # 工作中，会规定很多状态码，而每个状态码都对应一种操作结果
            # 在美多商城里如果QQ用户未绑定美多商城的用户，通过状态码300告诉前端，让他根据需求文档做响应的处理
        else:
            # openid已绑定美多商城的用户：直接实现状态保持即可
            # login(request=request,user="和openid绑定的美多商城的用户对象")
            # 在实现QQ登录时，真正登录到美多商城的不是QQ用户，而是QQ用户绑定的美多商城的用户
            login(request=request,user=oauth_model.user) # 相当于找到了OAuthQQUser.user，对应的是跟openid关联的用户对象
            response = http.JsonResponse({"code":0,"errmsg":"OK"})
            response.set_cookie("username",oauth_model.user.username,max_age=3600*24*14)
            return response

    def post(self,request):
        # 实现openid绑定用户逻辑

        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get("mobile")
        password = json_dict.get("password")
        sms_code_client = json_dict.get("sms_code")
        access_token = json_dict.get("access_token")

        # 2.校验参数
        if not all([mobile,password,sms_code_client,access_token]):
            return http.JsonResponse({"code":400,"errmsg":"缺少必传参数"})
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return http.JsonResponse({"code": 400, "errmsg": "mobiel有误"})
        if not re.match(r"^[a-zA-Z0-9_-]{8,20}$",password):
            return http.JsonResponse({"code":400,"errmsg":"password有误"})

        # 校验短信验证码（和user里的注册视图一样的，复用代码）
        redis_conn = get_redis_connection("verify_code")
        sms_code_server = redis_conn.get("sms_%s" % mobile)  # 在python3中，无论是读取还是存储到redis，都是bytes类型

        # 判断短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({"code": 400, "errmsg": "短信验证码过期"})
        # 对比用户输入的和服务端存储的短信验证码是否一致
        # 下面.decode()失效，所以单独转一下
        sms_code_server = sms_code_server.decode()
        # if sms_code_client != sms_code_server.decode():
        if sms_code_client != sms_code_server:
            return http.JsonResponse({"code": 400, "errmsg": "参数mobile有误"})

        # 校验openid
        openid = check_access_token_openid(access_token)
        if not openid:
            return http.JsonResponse({"code": 400, "errmsg": "openid有误"})


        # 3.判断手机号对应的用户是否存在
        # 用User模型类去查
        # 使用get时，通常用try捕获异常
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果手机号对应的用户不存在，新建用户
            # 这时新建的用户用户名是手机
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)
        else:
            # 如果手机号对应的用户已存在，校验密码
            if not user.check_password(password):
                return http.JsonResponse({"code":400,"errmsg":"密码有误"})

        # 4.如果手机号对应的用户不存在，创建用户
        #   如果手机号对应的用户存在，校验密码
        #   将上面得到的用户跟openid进行绑定即可
        # create_user():只有继承自AbstractUser的用户模型类才能去调用，创建用户记录
        # create():凡是继承自Model的模型类都可以调用，用来创建记录
        # 在美多商城项目中，只有User这个模型类才能调用create_user()，其他都不行
        try:
            OAuthQQUser.objects.create(user=user,openid=openid)
        except Exception as e:
            return http.JsonResponse({"code":400,"errmsg":"QQ登录失败"})

        # 5.实现状态保持
        login(request=request,user=user)
        response = http.JsonResponse({"code":0,"errmsg":"OK"})
        response.set_cookie("username",user.username,max_age=3600*24*14)
        # 6.响应结果
        return response
from django.shortcuts import render
from django.views import View
# 这里users.models 导入User，是从apps开始的，如果把目录写全，则Django不支持，所以只能这样写。
# 这样写pycharm又不支持，所以要把apps这个文件夹添加到导包路径中，右键 + Mark directory as + sources root
from apps.users.models import User,Address
from django import http
# 日志输出器导入
import logging,json,re
from django.contrib.auth import login,authenticate,logout
from django_redis import get_redis_connection
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_email_verify_url
from apps.users.utils import generate_email_verify_url,check_email_verify_url

# Create your views here.

# 日志输出器
logger = logging.getLogger("django")


# 用户注册
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
        # 提取短信验证码
        sms_code_client = json_dict.get("sms_code")


        # 校验参数
        # 1.判断是否缺少必传参数
        # all([]):判断某些数据中是否有空的数据,里面传列表数据
        # 只要列表中元素有任意一个为空，则返回False。只有所有的元素不为空，就返回True
        if not all([username,password,password2,mobile,allow,sms_code_client]):
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

        # 5.1 判断短信验证码是否正确：和图形验证码验证逻辑一致
        # 5.2 提取服务端存储的短信验证码
        redis_conn = get_redis_connection("verify_code")
        sms_code_server = redis_conn.get("sms_%s" % mobile)  #在python3中，无论是读取还是存储到redis，都是bytes类型
        # 5.3 判断短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({"code":400,"errmsg":"短信验证码过期"})
        # 5.4 对比用户输入的和服务端存储的短信验证码是否一致
        if sms_code_client != sms_code_server.decode():
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

        # 把username传入cookie供前端识别，会在页面右上角显示登陆状态
        response = http.JsonResponse({"code":0,"errmsg":"注册成功"})
        response.set_cookie("username",user.username,max_age=3600*24*14)
        # 响应结果：如果注册成功，前端会把用户引导到首页
        return response


# 判断用户名是否重复注册
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


# 判断手机号是否重复注册
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


# 用户登录
class LoginView(View):
    # POST /login/

    def post(self,request):
        # 实现用户登录逻辑
        # 接收参数
        json_dict = json.loads(request.body.decode())
        # 这里为了多账号登录，username改成account
        account = json_dict.get("username")
        password = json_dict.get("password")
        # 布尔类型，可真可假
        remembered = json_dict.get("remembered")

        # 校验参数
        if not all([account,password]):
            return http.JsonResponse({"code":400,"errmsg":"缺少必传参数"})
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
        #     return http.JsonResponse({"code": 400, "errmsg": "username格式错误"})
        if not re.match(r"^[a-zA-Z0-9_-]{8,20}$",password):
            return http.JsonResponse({"code":400,"errmsg":"password格式错误"})

        # 实现多账号登录   读源代码得来的方法，跟讲义不同  Newbee!
        # 判断用户输入的账号是用户名还是手机号，如果还有邮箱登录，那再加一个elif
        if re.match(r"^1[3-9]\d{9}$",account):
            # 用户输入的是手机号：将USERNAME_FIELD指定为“mobile”字段
            User.USERNAME_FIELD = "mobile"
        else:
            # 用户输入的是用户名：将USERNAME_FIELD指定为“username”字段
            User.USERNAME_FIELD = "username"


        # 实现核心逻辑
        # 认证登录用户：Django用户认证系统已经封装好了  authenticate
        # 认证仅仅是为了证明当前用户是美多商城之前的注册用户
        # 核心思想：先使用用户名作为条件去用户表查询该记录是否存在，如果该用户名对应的记录存在，再校验密码是否正确
        user = authenticate(request=request,username=account,password=password) #如果通过验证，则会返回用户名
        # 判断用户认证是否成功
        if not user:
            return http.JsonResponse({"code":400,"errmsg":"用户名或密码错误"})  #不能告诉哪里错误，不然容易被黑客利用

        # 实现状态保持（加标记）
        login(request,user)
        # 还需要根据remembered参数去设置状态保持的周期
        # 如果用户选择了记住登录，那么状态保持周期为两周，反之，浏览器会话结束状态保持就销毁
        if remembered:
            # 记住登录：设置session数据的过期时间
            # set_expiry(None):Django封装好的，默认两周
            # 如果自己写时间，则按秒算
            request.session.set_expiry(None)
        else:
            # 没有记住登录
            request.session.set_expiry(0)

        # 把username传入cookie供前端识别，会在页面右上角显示登陆状态
        response = http.JsonResponse({"code":0,"errmsg":"OK"})
        response.set_cookie("username",user.username,max_age=3600*24*14)

        # 响应结果
        return response

class LogoutView(View):
    # 退出登录 DELETE /logout/

    def delete(self,request):
        # 逻辑与登录相反，登录成功后是记住状态，退出登录时是清理登录状态
        # 登录成功后将用户名写入cookie，退出登录时清理cookie中用户名
        # 清理登录状态
        logout(request)
        # 清理用户名cookie
        response = http.JsonResponse({"code":0,"errmsg":"退出登录成功"})
        response.delete_cookie("username")
        return response


class UserInfoView(LoginRequiredJSONMixin,View):
    # 用户中心数据展示
    def get(self,request):
        #         # 用户基本信息展示
        #         # 由于我们在该接口中，判断了用户是否是登录用户
        #         # 所以能够进入到该接口的请求，一定是登录用户发送的
        #         # ∴request.user里面获取的用户信息一定是当前登录的用户信息
        # 可以查看AuthenticationMiddleware源代码，里面封装了这块的逻辑
        # （Django拿着session中提取的user_id，去数据库查询出来的user信息，赋值给了request.user）
        # 技巧:如果该接口只有登录用户可以访问，那么在接口内部可以直接使用request.user获取当前登录用户信息
        data_dict = {
                    "code": 0,
                    "errmsg": "OK",
                    "info_data": {
                        "username": request.user.username,
                        "mobile": request.user.mobile,
                        "email": request.user.email,
                        "email_active": request.user.email_active,
                    },
                }
        return http.JsonResponse(data_dict)

# 不用再重写一次这个类，因为Django已经定义了，所以直接让已经定义的类作为父类即可。如上
# class UserInfoView(View):
#     # 用户中心
#     # GET /info/
#     def get(self,request):
#         # 用户中心数据展示
#         # 判断用户是否登录的逻辑，是在请求进入视图之后判断的
#         # 而Django的扩展类-【LoginRequiredMixin】则是在路由分发时就在判断了
#         # 使用is_autenticated属性判断是否登录
#         if not request.user.is_authenticated:
#             # False未登录
#             return http.JsonResponse({"code": 400, "errmsg": "用户未登录"})
#         # True已登录
#         # 因为前端文件写的需要返回这些数据，所以要定义这些
#         data_dict = {
#             "code": 0,
#             "errmsg": "OK",
#             "info_data": {
#                 "username": "",
#                 "mobile": "",
#                 "email": "",
#                 "email_active": "",
#             }
#         }
#         return http.JsonResponse(data_dict)

class EmailView(LoginRequiredJSONMixin,View):
    # 添加邮箱
    # PUT /emails/

    def put(self,request):
        #实现添加邮箱逻辑
        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get("email")

        # 2.校验参数
        if not email:
            return http.JsonResponse({"code":400,"errmsg":"缺少必传参数"})
        # 校验邮箱格式
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$",email):
            return http.JsonResponse({"code":400,"errmsg":"参数email有误"})
        # 3.实现核心逻辑:添加邮箱就是将用户填写的邮箱地址保存到当前登录用户的email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"code":400,"errmsg":"添加邮箱失败"})

        # 发送邮箱的验证激活邮件
        # 耗时操作，不能让它阻塞主逻辑，需要解耦出去，用celery完成
        # send_email_verify_url.delay(email,"激活链接")
        # verify_url = "封装一个工具方法，专门生成激活链接，放在apps.user里"
        verify_url = generate_email_verify_url(user=request.user) #传参不能直接user，当前登录用户.user即可
        send_email_verify_url.delay(email,verify_url)

        # 4.响应结果
        return http.JsonResponse({"code":0,"errmsg":"OK"})

# 验证激活邮箱
class EmailActiveView(View):
    # PUT  /email/verification/
    def put(self,request):
        # 核心逻辑：将email_active变为True
        # 1.接收参数
        token = request.GET.get("token")
        # 2.校验参数
        if not token:
            return http.JsonResponse({"code":400,"errmsg":"缺少必传参数"})

        # 3.实现核心逻辑：通过token提取要验证邮箱的用户-->将要验证邮箱的用户的email_active字段设置为True
        user = check_email_verify_url(token=token)
        try:
            user.email_active = True
            user.save() #同步到数据库
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"code":400,"errmsg":"邮箱验证失败"})

        # 4.响应结果
        return http.JsonResponse({"code": 0, "errmsg": "邮箱验证成功"})


# 新增收货地址
class CreateAddressView(LoginRequiredJSONMixin,View):
    # POST /addresses/create/

    def post(self,request):
        # 实现新增地址的逻辑

        # 补充逻辑:在每次新增地址前,我们都要判断当前登录用户未被逻辑删除的地址数量是否超过了上限20
        # 核心:查询出当前登录用户未被逻辑删除地址数量
        # 逻辑：一查多
        try:
            count = request.user.addresses.filter(is_deleted=False).count()
        except Exception as e:
            return http.JsonResponse({"code":400,"errmsg":"获取数据库中的地址个数出错"})
        # 判断是否超过上限
        if count >= 20:
            return http.JsonResponse({"code":400,"errmsg":"地址数量超过上限"})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel') # 非必传
        email = json_dict.get('email') # 非必传
        # 校验参数
        # 说明：province_id,city_id,district_id在这里不需要校验
        # 这里的校验仅仅是校验数据格式是否满足要求，省市区的参数传过来的是外键，外键自带约束和校验
        # 如果外键错误，在赋值时会自动抛出异常，在赋值时可以捕获异常校验
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': 400,'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': 400,'errmsg': '参数email有误'})

        # 实现核心逻辑：将用户填写的地址数据保存到地址数据表
        try:
            address = Address.objects.create(
                # 外键赋值有两种形式：
                    #id对应id：user_id = request.user.id
                    #属性对应对象（具体的值）：user = request.user
                user = request.user, # 或者 user_id = request.user.id
                province_id = province_id,  # province 是模型类中的属性，在表中表现为province_id。因为前端传回来只有id信息
                city_id = city_id,
                district_id = district_id,
                title = receiver, # 默认地址的标题就是收件人
                receiver = receiver,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email,
                # 实际还有个on_delete，默认False不需要赋值
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"code":400,"errmsg":"新增地址失败"})

        # 补充逻辑：在新增地址时，给用户绑定一个默认地址，为了保证用户一创建地址就有默认地址
        # 判断当前用户是否已有默认地址
        # 如果没有默认地址，就把当前的地址作为该用户的默认地址
        if not request.user.default_address:
            request.user.default_address = address
            # request.user.default_address_id = address.id  也可
            request.user.save()

        # 响应结果：为了让新增地址成功后，页面可以及时展示新增的地址，我们会将新增的地址响应给前端渲染
        # 构造要响应的数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({"code":0,"errmsg":"OK","address":address_dict}) # 响应的是一个字典

# 获取收货地址
class AddressView(LoginRequiredJSONMixin,View):
    # GET /addresses/

    def get(self,request):
        # 查询收货地址
        # 核心逻辑：查询当前登录用户未被逻辑删除的地址
        address_model_list = request.user.addresses.filter(is_deleted=False)

        # 查询当前登录用户默认地址ID
        default_address_id = request.user.default_address_id

        # 将地址模型列表转字典列表
        addresses = []
        for address in address_model_list:
            address_dict = {
                "id":address.id,
                "title":address.title,
                "receiver":address.receiver,
                "province":address.province.name,
                "city":address.city.name,
                "district":address.district.name,
                "place":address.place,
                "mobile":address.mobile,
                "tel":address.tel,
                "email":address.email,
            }
            addresses.append(address_dict)

        return http.JsonResponse({
            "code":0,
            "errmsg":"OK",
            "default_address_id":default_address_id,
            "addresses":addresses,
        })





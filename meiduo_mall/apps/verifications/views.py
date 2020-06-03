from django.shortcuts import render
from django.views import View
from apps.verifications.libs.captcha.captcha import captcha#接收参数用的
from django_redis import get_redis_connection
from django import http
import random,logging
from apps.verifications.libs.yuntongxun.ccp_sms import CCP

from celery_tasks.sms.tasks import ccp_send_sms_code
# Create your views here.

# 创建日志输出器
logger = logging.getLogger("django")

class ImageCodeView(View):
    # GET http://www.meiduo.site:8000/image_codes/xxxx/
    def get(self,request,uuid):
        # 实现图像验证码逻辑
        # :param uuid:uuid
        # return:image/jpg
        # 接收参数,校验参数
        # 1.生成图形验证码
        text,image = captcha.generate_captcha()

        # 2.保存图形验证码
        # 使用配置的Redis数据库的别名，创建连接到redis的对象
        redis_conn = get_redis_connection("verify_code")
        # 使用连接到redis的对象去操作数据存储到redis
        # redis_conn.set("key","value") --》没有有效期，所以不用它
        # 图形验证码必须要有有效期:300s
        # redis_conn.setex("key","过期时间","value")
        redis_conn.setex("img_%s" % uuid,300,text)

        # 3.响应图形验证码
        return http.HttpResponse(image,content_type="image/jpg")

# 手机验证码
class SMSCodeView(View):
    # 短信验证码
    # GET /sms_codes/xxx/
    def get(self,request,mobile):
        # 实现发送短信验证码的逻辑
        # param:mobile手机号
        # return:JSON

        # 我们为了尽早检查出该手机号是否频繁发送短信验证码，所以在逻辑开始的时候进行校验（节省服务器资源）
        # 提取出之前给某手机号绑定的标记
        redis_conn = get_redis_connection("verify_code")
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        # 判断标记是否存在，如果存在，响应错误信息，终止逻辑
        if send_flag:
            return http.JsonResponse({"code":400,"errmsg":"请勿频繁发送短信验证码"})

        # 接收参数：mobile(路径参数)、image_code(用户输入的图形验证码)、image_code_id(UUID)
        image_code_client = request.GET.get("image_code")  #切记中间的GET都是大写
        uuid = request.GET.get("image_code_id")

        # 校验参数
        # 判断是否缺少必传参数
        if not all([image_code_client,uuid,mobile]):
            return http.JsonResponse({"code":400,"errmsg":"缺少必传参数"})
        # 单个校验参数：image_code（用户输入的图形验证码）、image_code_id(UUID)


        # 实现核心逻辑
        # 提取图形验证码：以前如何存，现在就如何读取
        redis_conn = get_redis_connection("verify_code")
        image_code_server = redis_conn.get("img_%s" % uuid)
        # 判断图形验证码是否过期
        if not image_code_server:
            return http.JsonResponse({"code":400,"errmsg":"图形验证码失效"})
        # 删除图形验证码：为了防止恶意用户的恶意测试该图形验证码，我们要保证每个图形验证码只能使用一次
        redis_conn.delete("img_%s" % uuid)
        # 对比图形验证码：判断用户输入的图形验证码和服务端存储的图形验证码是否一致
        # image_code_server是bytes类型的数据，而image_code_client是str类型，不能直接比较。所以将xxx_server转换成str类型
        # decode():专门将bytes类型的字符串转换成str类型的字符串
        image_code_server = image_code_server.decode()
        # 为了提升用户体验，可以将图形验证码的文字，统一大小写(.lower()或.upper())
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({"code":400,"errmsg":"图形验证码有误"})

        # 生成短信验证码：美多商城短信验证码格式（随机六位数）
        # random.randint("范围起点"，"范围终点")
        # 如果不满足六位数，则在前面补0
        random_number = random.randint(0,999999)
        sms_code = "%06d" % random_number
        logger.info(sms_code)

        # 保存短信验证码：redis的2号库是专门保存图形和短信验证码的，也是300s有效期
        redis_conn = get_redis_connection("verify_code")
        # redis_conn.setex("key","expire","value")
        # redis_conn.setex("sms_%s" % mobile,300,sms_code)
        #
        # # 发短信前，给该手机号码添加有效期为60秒的标记,标记名字是1
        # redis_conn.setex("send_flag_%s" % mobile,60,1)

        # 使用pipeline管道来操作redis数据库的数据写入
        # 一般用于数据写入时
        # 创建pipeline管道
        pl = redis_conn.pipeline()
        # 使用管道将请求添加到队列
        pl.setex("sms_%s" % mobile, 300, sms_code)
        # 发短信前，给该手机号码添加有效期为60秒的标记,标记名字是1
        pl.setex("send_flag_%s" % mobile, 60, 1)
        # 执行管道
        pl.execute()

        # 发送短信验证码：对接容联云通讯的短信SDK，复制下面这行代码，导入需要包即可
        # CCP().send_template_sms('18123616680', ['习大大发来贺电', 5], 1)
        # 我们不需要判断发短信成功与否，所以不用接收发短信的返回值，判断其是否成功发送
        # 该方式是同步发送短信，发短信延迟则响应也延迟
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 使用celery的异步任务发送短信验证码
        # ccp_send_sms_code(mobile,sms_code)  #这种还是同步执行函数，不是celery的异步形式

        # 异步函数.delay（“参数”）：表示代码执行到这，该函数不要立即执行，先放行，让下一个代码执行
        # delay是celery封装的方法，只能用在celery中
        ccp_send_sms_code.delay(mobile,sms_code)

        # 响应结果
        return http.JsonResponse({"code":0,"errmsg":"发送短信验证码成功"})




from django.shortcuts import render
from django.views import View
from apps.verifications.libs.captcha.captcha import captcha#接收参数用的
from django_redis import get_redis_connection
from django import http
# Create your views here.
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


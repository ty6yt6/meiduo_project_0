from django.contrib import admin
from django.urls import path
from . import views
from .models import User

urlpatterns = [
    # \w:匹配非特殊字符，即a-z、A-Z、0-9、_、汉字
    # path("usernames/<"匹配用户名的路由转换器：变量">/count/",views.UsernameCountView.as_view())
    path("usernames/<username:username>/count/",views.UsernameCountView.as_view()),
    # 判断手机号是否重复添加路由
    # path("mobiles/(?P<mobile>1[3-9]\d{9})/count/",views.MobileCountView.as_view()),
    path("mobiles/<mobile:mobile>/count/",views.MobileCountView.as_view()),
    path("register/",views.RegisterView.as_view()),
    path("login/",views.LoginView.as_view()),
    path("logout/",views.LogoutView.as_view()),
    path("info/",views.UserInfoView.as_view()),
]
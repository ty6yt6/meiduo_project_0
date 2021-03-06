"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# 导入include
from django.urls import path,include

# 总路由中注册路由转换器
from django.urls import register_converter
from meiduo_mall.utils.converters import UsernameConverter,MobileConverter

register_converter(UsernameConverter,"username")
register_converter(MobileConverter,"mobile")

urlpatterns = [
    path('admin/', admin.site.urls),
    # 注册子应用users
    path("",include("apps.users.urls")),

    # 注册子应用verifications
    path("",include("apps.verifications.urls")),

    path("",include("apps.oauth.urls")),

    path("",include("apps.areas.urls")),

    # 首页测试查询列表
    path("",include("apps.contents.urls")),

    path("",include("apps.goods.urls")),
]

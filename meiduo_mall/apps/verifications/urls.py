from django.urls import path
from . import views

urlpatterns = [
    # 图形验证码：GET  http://www.meiduo.site:8000/image_codes/xxxx/
    # path("image_codes/<路由转换器uuid:变量名uuid>/",...)
    path("image_codes/<uuid:uuid>/",views.ImageCodeView.as_view()),
]
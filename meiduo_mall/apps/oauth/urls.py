from django.urls import path
from . import views

urlpatterns = [
    # qq登录扫码链接:GET /qq/authorization/
    path("qq/authorization/",views.QQURLView.as_view()),
    path("oauth_callback/",views.QQUserView.as_view()),
]
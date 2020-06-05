from django.shortcuts import render
from django.views import View
# Create your views here.
class QQURLView(View):
    # QQ登录扫码链接
    # GET /qq/authorization/
    def get(self,request):
        # 提供QQ登录扫码链接
        
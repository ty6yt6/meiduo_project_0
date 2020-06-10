from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django import http
from django.core.cache import cache
# Create your views here.

# 查询省份数据，公共接口，不需要判断用户是否登录
class ProvinceAreasView(View):
    # GET /areas/

    def get(self,request):

        # 读取缓存：如果在逻辑最开始时读取到缓存，则后面的逻辑不执行
        province_dict_list = cache.get("province_list")
        if province_dict_list:
            return http.JsonResponse({"code":0,"errmsg":"OK","province_list":province_dict_list})

        # 实现查询省份数据的逻辑
        # 查询省份数据
        # Area.objects.all() 查询所有的省市区
        # Area.objects.get() 只能查一个
        # 查询一个列表内的顶级数据，直接查没有父级的数据就可
        province_model_list = Area.objects.filter(parent=None)
        # 重要提示：JsonResponse()不识别模型数据（模型对象和查询集），它只识别字典、列表和字典列表
        # province_model_list 就是个查询集，所以需要将查询集模型列表转换成字典列表
        province_dict_list = []
        for province_model in province_model_list:
            # 模型数据转字典
            province_dict = {
                "id":province_model.id,
                "name":province_model.name,
            }
            province_dict_list.append(province_dict)

        # 需要缓存省份字典列表
        # cache.set("key","value","过期时间（秒）")
        cache.set("province_list",province_dict_list,3600)


        return http.JsonResponse({
            "code":0,
            "errmsg":"OK",
            "province_list":province_dict_list
        })

# 查询城市或区县数据
class SubAreasView(View):
    # GET /areas/编号/
    # 说明：省市区的数据，不是用户必须交互或者必须得到结果的，没有数据就可以不用管（弹窗）
    # 如果希望项目中的任何错误，都在日志中输出，这个时候就可以try
    # 在开发时，遇到任何的数据库的错误，都必须try，这样做更加严谨
    def get(self,request,parentid):
        # 实现查询城市或者区县数据的逻辑
        # :param parentid:省份ID，城市ID
        # return:城市数据、区县数据
        # 说明：如果传递的是省份ID，就查城市数据；如果是城市数据，就查区县数据

        # 读取缓存
        sub_data = cache.get("sub_data_%s" % parentid)
        if sub_data:
            return http.JsonResponse({"code":0,"errmsg":"OK","sub_data":sub_data})

        # 查询当前父级地区：省份或城市
        parent_area = Area.objects.get(id=parentid)
        # 查询当前父级地区的子集（一查多）：省份查城市、城市查区县，要查询父级对应的所有子集
        sub_model_list = parent_area.subs.all()

        # 将子集模型列表转为字典列表
        subs = []
        for sub_model in sub_model_list:
            sub_dict = {
                "id":sub_model.id,
                "name":sub_model.name,
            }
            subs.append(sub_dict)
        sub_data = {
            "id":parent_area.id,
            "name":parent_area.name,
            "subs":subs, # 子集字典列表
        }

        # 缓存子级数据
        # 对于子级的缓存，我们需要区分当前缓存的是哪个父级的子级
        # 如：需要区分当前缓存的是哪个省的城市
        # 如果不区分，则数据会被覆盖
        cache.set("sub_data_%s" % parentid,sub_data,3600)

        return http.JsonResponse({
            "code":0,
            "errmsg":"OK",
            "sub_data":sub_data,
        })












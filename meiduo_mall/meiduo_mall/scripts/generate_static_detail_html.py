#!/usr/bin/env python
# 第一行指定python解释器
# 脚本文件，可以脱离Django独立运行。为了生成网页静态化页面，可以参考manage.py脚本文件

# 指定导包路径：是为了后面的导包按照美多商城的导包方式正常导包
import sys
# sys.path.insert(导包路径列表的角标，0表示新的导包路径在最前面，"新的导包路径，这里是指向第一个meiduo_mall")
# 指向第一个meiduo_mall：从当前的scripts文件目录网上回退两级即可
sys.path.insert(0,"../../")

# 设置Django运行所依赖的环境变量
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')


# 让Django进行一次初始化
import django
django.setup()

# 导入所需要的依赖包、相关模型类
from django.template import loader
from django.conf import settings
from apps.goods.goods_utils import get_categories,get_breadcrumb,get_goods_specs
from apps.goods.models import SKU

# 定义静态化详情页的工具方法
def action_static_detail_html(sku):
    """
    :param sku:要静态化的SKU信息
    """
    # 查询要渲染页面的数据
    # 查询商品SKU信息：参数sku
    # 查询商品分类
    categories = get_categories()
    # 查询面包屑导航
    breadcrumb = get_breadcrumb(sku.category)
    # 查询商品规格信息
    goods_specs = get_goods_specs(sku)
    # 查询SKU关联的SPU，渲染商品详情，售后，包装：SPU信息可以在模板中通过关联查询得到{{ sku.spu }}，所以在这不写
    # 构造上下文字典
    context = {
        "sku":sku,
        "categories":categories,
        "breadcrumb":breadcrumb,
        "goods_specs":goods_specs,
    }
    # 使用上下文字典渲染详情页HTML文件，并得到详情页的HTML字符串
    template = loader.get_template("detail.html")
    detail_html_str = template.render(context)

    # 将详情页的HTML字符串写入到指定的静态文件中
    # file_path = "路径/front_end_pc/goods/3.html"
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR),"front_end_pc/goods/"+str(sku.id)+".html")
    with open(file_path,"w",encoding="utf-8") as f:
        f.write(detail_html_str)

if __name__ == '__main__':
    # 脚本入口：查询所有的sku信息，遍历它们，每遍历一个sku就生成一个对应的静态页
    skus = SKU.objects.all()
    for sku in skus:
        # print(sku.id)
        action_static_detail_html(sku)
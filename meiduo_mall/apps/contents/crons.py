# 静态化首页的工具
from apps.contents.models import GoodsChannel,ContentCategory
from django.template import loader
from django.conf import settings
import os
def generate_static_index_html():
    # 生成静态的首页HTML文件
    # 准备商品分类数据的字典容器
    categories = {}

    # 查询所有的37个频道（一级分类）
    # GoodsChanel.objects.all().order_by("group_id","sequence")
    channels = GoodsChannel.objects.order_by("group_id", "sequence")

    # 遍历所有频道，取出每一个频道
    for channel in channels:
        # 通过频道数据关联的组取出对应的组号
        group_id = channel.group.id
        # 将group_id作为categories字段的key
        if group_id not in categories:
            categories[group_id] = {"channels": [], "sub_cats": []}
        # 获取当前频道关联的一级分类（一个频道对应一个一级分类）
        cat1 = channel.category
        # 添加每组中对应的频道数据
        categories[group_id]["channels"].append({
            "id": channel.id,
            "name": cat1.name,
            "url": channel.url,
        })

        # 添加每组中的二级和三级分类
        for cat2 in cat1.subs.all():
            # 使用二级分类查询关联的三级分类
            sub_cats = []
            for cat3 in cat2.subs.all():
                sub_cats.append({
                    "id": cat3.id,  # 三级分类id
                    "name": cat3.name,  # 三级分类名字
                })
            categories[group_id]["sub_cats"].append({
                "id": cat2.id,  # 二级分类id
                "name": cat2.name,  # 二级分类名字
                "sub_cats": sub_cats,
            })

    # 查询首页广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for content_cat in content_categories:
        # 在遍历的过程中，取出每一种广告关联的广告内容
        # 一查多语法：一方模型对象.一查多关联字段
        # 过滤：能展示的广告状态都是True（1）
        contents[content_cat.key] = content_cat.content_set.filter(status=True).order_by("sequence")

    # 构造渲染html页面的上下文字典
    context = {
        "categories":categories, # 商品分类
        "contents":contents, # 首页广告
    }

    # 渲染页面数据，并得到页面对应的HTML字符串
    # 1.获取文件目录templates中index.html
    template = loader.get_template("index.html")
    # 2.使用上下文字典context的数据 去渲染index.html
    index_html_str = template.render(context)
    # 将渲染好的HTML字符串保存到静态HTML文件中
    # with open("file_path","w",encoding="utf-8") as f:
        # f.write(index_html_str)
    # file_path = os.path.join(os.path.dirname(os.path.dirname(settings.BASE_DIR)),"front_end_pc/index.html")
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR),"front_end_pc/index.html")
    with open(file_path,"w",encoding="utf-8") as f:
        f.write(index_html_str)

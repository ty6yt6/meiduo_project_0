# celery的入口文件
from celery import Celery

# 在创建celery实例之前，把Django的配置模块加载到运行环境中（不加载Django配置模块就不能用Django里的东西）
# 加载的Django配置模块要在celery的启动文件中
import os
if not os.getenv("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"



# 创建celery实例
# Celery("别名")
celery_app = Celery("meiduo")
# 加载配置
# celery_app.config_from_object("配置文件")
celery_app.config_from_object("celery_tasks.config")

# 注册异步任务
# 地址写到sms(文件夹)即可，celery会自动在sms中寻找tasks文件，并且找到所有被@celery_app.task()装饰的函数进行导入
celery_app.autodiscover_tasks(["celery_tasks.sms","celery_tasks.email"])

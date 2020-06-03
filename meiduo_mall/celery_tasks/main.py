# celery的入口文件
from celery import Celery
# 创建celery实例
# Celery("别名")
celery_app = Celery("meiduo")
# 加载配置
# celery_app.config_from_object("配置文件")
celery_app.config_from_object("celery_tasks.config")

# 注册异步任务
# 地址写到sms即可，celery会自动在sms中寻找tasks文件，并且找到所有被@celery_app.task()装饰的函数进行导入
celery_app.autodiscover_tasks(["celery_tasks.sms"])
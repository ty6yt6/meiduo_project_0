# 定义任务的文件
# celery中所有的任务，本质就是一个标准的python函数
# celery要使用的文件，要在自己的包中保管
from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from celery_tasks.main import celery_app
# 需要celery提供的装饰器装饰该函数，让celery可以识别该函数
# celery_app.task(name=“别名”)
@celery_app.task(name="ccp_send_sms_code")
def ccp_send_sms_code(mobile,sms_code):
    # 发短信的异步任务
    # param mobile:手机号
    # param sms_code:短信验证码
    # return:成功（0），失败（1）
    ret = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    return ret

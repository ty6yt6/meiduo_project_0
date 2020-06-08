from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
from django.conf import settings
from apps.users.views import User
# 生成邮箱激活链接
def generate_email_verify_url(user):
    # 生成邮箱激活链接
    # :param user:当前要添加并验证邮箱的登录用户
    # :return：邮箱激活链接
    # 1.创建序列化器对象
    s = Serializer(settings.SECRET_KEY,3600*24)
    # 2.准备要序列化的数据
    data = {"user_id":user.id,"email":user.email}
    # 3.序列化
    token = s.dumps(data).decode()
    # 4.返回邮箱激活链接
    verify_url = settings.EMAIL_VERIFY_URL + token
    return verify_url

# 反序列化用户信息密文
def check_email_verify_url(token):
    # :param token:用户信息密文
    # :return 用户对象信息

    # 创建序列化器对象(和加密时用的序列化器一样)
    s = Serializer(settings.SECRET_KEY,3600*24)
    # 反序列化
    try:
        data = s.loads(token)
    except BadData:
        return None
    else:
        # 提取用户信息
        user_id = data.get("user_id")
        email = data.get("email")
        # 使用user_id和email查询对应的用户对象
        try:
            user = User.objects.get(id=user_id,email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
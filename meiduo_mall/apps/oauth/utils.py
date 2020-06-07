# 对openid进行序列化和反序列化（加密）
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
from django.conf import settings
# settings是配置模块，启动后端服务器则对应div，启动前端则对应wsgi，总之导入它，设置里的东西都能读取到
# 这里要用的是dev中的  SECRET_KEY = '&g%#4y#&%kmeiaplx7u%6prik^f&l8=q%^xoz^#ss7s&t$y$+-'

def generate_access_token_openid(openid):
    # 序列化openid
    # param：openid的明文
    # return：openid的密文字符串

    # 1.创建序列化器对象
    s = Serializer(settings.SECRET_KEY,600)
    # 2.构造要序列化数据
    data = {"openid":openid}
    # 3.返回密文字符串：将bytes类型的token转成字符串类型的数据
    token = s.dumps(data)
    return token.decode()

def check_access_token_openid(access_token):
    # 反序列化openid
    # param：access_token（密文字符串形式的openid）
    # return:明文openid
    # 1.创建一个相同的序列化器对象
    s = Serializer(settings.SECRET_KEY, 600)
    # 2.反序列化
    try:
        data = s.loads(access_token)
    except BadData:
        return None
    # 3.读取openid明文
    openid = data.get("openid")
    # 4.返回openid明文
    return openid
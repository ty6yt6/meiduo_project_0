# 自定义文件存储类，提供文件下载的全路径
from django.core.files.storage import Storage
from django.conf import settings
# 自定义文件存储类（所以用的时候一定要在父类默认设置的路径那项改类路径，原路径在globalsetting里，但是只需要在dev中加上新的就可以改了）
class FastDFSStorage(Storage):

    def _open(self,name,mode="rb"):
        """
        Django要求继承自Storage的类，必须有_open这个私有方法
        打开文件时自动调用的，而当前不是打开文件，但是文档要求这么写，所以什么都不做，直接pass
        :param name: 要打开的文件名
        :param mode: 打开文件的模式
        :return: None
        """
        pass

    def _save(self,name,content):
        """
        Django要求继承自Storage的类，必须有_save这个私有方法
        保存文件时自动调用的，而当前不需要保存文件，但是文档要求这么写，所以什么都不做，直接pass
        :param name:
        :param content:
        :return:
        """
        pass

    # 重写父类中的url，让它返回全路径
    # 调用这个url是另一个url方法调用的，所以如果想让前端默认调用这个url，则需index中所有image点出url，即image.url
    def url(self,name):
        """
        返回文件下载全路径的方法
        :param name: 外界的image字段传入到文件名：file_id（例：group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396）
        :return:http://192.168.254.168:8888/group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396
        """
        # return "http://192.168.254.168:8888/" + name
        return settings.FDFS_URL + name
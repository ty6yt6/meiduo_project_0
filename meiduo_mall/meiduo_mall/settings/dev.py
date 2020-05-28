# 开发时使用的配置文件，代替settings.py

"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&g%#4y#&%kmeiaplx7u%6prik^f&l8=q%^xoz^#ss7s&t$y$+-'

# SECURITY WARNING: don't run with debug turned on in production!
# 先改为False测试
DEBUG = False

ALLOWED_HOSTS = ["*",
    # 'api.beautymall.site',
    # '127.0.0.1',
    # 'localhost',
    # 'www.beauty.site',
    # "www.meiduo.site",

]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',#django默认的用户认证系统：里面处理完了跟用户相关的一切操作
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 用户模块注册
    # 导包路径：决定如何通过包路径找到对应的包，任何python项目都有，meiduo_mall也是导包路径，所以直接apps.users
    # 查看导包路径：import sys print(sys.path)
    "apps.users"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

# 配置模板
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        "HOST":"192.168.254.158",
        "PORT": 3306,
        "USER": "zjw",
        "PASSWORD": "ty6yt6",
        "NAME":"meiduo_mall_6",
    }
}

# 配置 Redis
# 以后还会追加购物车、浏览记录等项目
CACHES = {
    "default": { # 默认存储信息: 存到 0 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.254.157:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 将session存储在Redis的1号库
    "session": { # session 信息: 存到 1 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.254.157:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# 配置session后端
SESSION_ENGINE = "django.contrib.sessions.backends.cache"#修改为redis存储session
SESSION_CACHE_ALIAS = "session"#存储session数据时使用的配置别名

# 配置日志信息，格式固定且通用
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,#300MB/个日志文件
            'backupCount': 10,#最多创建10个日志文件
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'


# 指定Django程序默认的用户模型类为自定义的用户模型类
# AUTH_USER_MODEL = 'auth.User'  为Django默认的User
# AUTH_USER_MODEL = “子应用.自定义的用户模型类”
# 指定完用户模型类后，要迁移后才能使用
AUTH_USER_MODEL = 'users.User'
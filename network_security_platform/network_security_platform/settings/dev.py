"""
Django settings for network_security_platform project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os, time
import datetime
from pathlib import Path
import user_app

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-53qfs267k*2kvd@xnc&+59n!&p$#ugr_h)l979@9@3m9ovqci8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# ============================== Application definition ======================================
INSTALLED_APPS = [
    'corsheaders',  # 跨域CORS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # DRF 框架
    'rest_framework_jwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',  # 生成API接口
    'channels',  # WebSocket连接
    'user_app',  # 用户模块子应用
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Cors
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.blacklist_check.blacklist_check_middleware'
]

# ==================================== JWT =======================================
# 设置分页器
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': (
        # 配置认证方式的选项 DRF的认证是内部循环遍历每一个注册的认证类
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'PAGE_SIZE': 10
}


# JWT配置
JWT_AUTH = {
    # 设置 JWT 的过期时间
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 设置 JWT 的响应格式
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'utils.jwt_handler.jwt_response_handler',
    'JWT_ALGORITHM': 'HS256',
    'JWT_SECRET_KEY': SECRET_KEY,
}

SIMPLE_JWT = {
    'BLACKLIST_AFTER_ROTATION': True,
}

# ==================================== CORS ========================================
# 设置允许的header
CORS_ALLOW_HEADERS = [
    '*'
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# 设置CORS白名单，凡是出现在白名单中的域名，都可以访问后端接口
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.5.4:3000',
    'http://localhost:9090',
)

CORS_ALLOW_CREDENTIALS = True # 允许携带cookie

# ==================================================================================

ROOT_URLCONF = 'network_security_platform.urls'

WSGI_APPLICATION = 'network_security_platform.wsgi.application'

# 添加自定义用户模型类（应用名.模型类名）
AUTH_USER_MODEL = 'user_app.UserBaseInfoModel'

# ==================================== jinja2 ======================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  #jinja2模板引擎
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {  # 因jinja2不能直接使用context_processor
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充Jinja2模板引擎环境
            'environment': 'utils.jinja2_env.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# ==================================== Database =======================================
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MySQL数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'network_security_platform_db',
        'USER': 'root',
        'PASSWORD': 'rrxx220605.',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 配置Redis数据库
CACHES = {
    "default": {  # 默认
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": {  # 验证码
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "blacklist": {  # Token 黑名单
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


# ================================= Password validation ==============================
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# ================================ Internationalization =====================================
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

# ====================================== Logging ===================================
# 配置项⽬日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, # 是否禁用已经存在的日志器
    'formatters': { # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(filename)s: %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': { # 对日志进行过滤
        'require_debug_true': { # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': { # ⽇志处理⽅法
        'console': { # 向终端中输出日志
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    'file': { # 向文件中输出日志
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs/nsp.log'), # 日志⽂件的位置
        'maxBytes': 300 * 1024 * 1024,
        'backupCount': 10,
        'formatter': 'verbose'
        },
    },
    'loggers': { # 日志器器
        'django': { # 定义了⼀一个名为django的⽇日志器器
            'handlers': ['console', 'file'], # 可以同时向终端与⽂文件中输出⽇日志
            'propagate': True,# 是否继续传递日志信息
            'level': 'INFO',# 日志器器接收的最低⽇志级别
        },
    }
}

# ================================== MEDIA_SETTING =================================
# 配置 MEDIA_ROOT 作为上传文件在服务器中的基本路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')
# 配置 MEDIA_URL 作为公用 URL，指向上传文件的基本路径
MEDIA_URL = '/upload/'

# ===================================== SMS ========================================
# 容联云短信验证码参数
accId = '2c94811c8853194e0188616ffbeb0324'
accToken = '35a494f497cd4f37989b879a61a35602'
appId = '2c94811c8853194e0188616ffd23032b'

# ===================================== ASGI =======================================
# 实现前后端数据的传递
ASGI_APPLICATION = 'network_security_platform.asgi.application'

# ==================================================================================

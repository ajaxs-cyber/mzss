"""
Django settings for mzss_v2 project.

觅知音 - 音乐场景量化匹配系统

支持 SQLite（开发环境）和 PostgreSQL（生产环境）自动切换。
包含 CORS、REST Framework、WhiteNoise 等完整配置。
"""

import os
from pathlib import Path

# ── 路径配置 ──
BASE_DIR = Path(__file__).resolve().parent.parent

# ── 安全密钥 ──
# 生产环境请通过环境变量设置：DJANGO_SECRET_KEY
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-change-me-in-production-mzss-v2-secret-key-2024",
)

# ── 调试模式 ──
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

# ── 允许的主机 ──
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,mzss.onrender.com"
).split(",")


# ═══════════════════════════════════════════
# 1. INSTALLED_APPS
# ═══════════════════════════════════════════

INSTALLED_APPS = [
    # Django 内置
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 第三方
    "rest_framework",
    "django_filters",
    "corsheaders",
    # 本地应用
    "core",
]


# ═══════════════════════════════════════════
# 2. MIDDLEWARE
# ═══════════════════════════════════════════

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",           # CORS（放最前面）
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",      # WhiteNoise 静态文件
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ═══════════════════════════════════════════
# 3. URL 配置
# ═══════════════════════════════════════════

ROOT_URLCONF = "mzss.urls"


# ═══════════════════════════════════════════
# 4. 模板配置
# ═══════════════════════════════════════════

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ═══════════════════════════════════════════
# 5. WSGI 应用
# ═══════════════════════════════════════════

WSGI_APPLICATION = "mzss.wsgi.application"


# ═══════════════════════════════════════════
# 6. 数据库配置（SQLite / PostgreSQL 自动切换）
# ═══════════════════════════════════════════

# 通过环境变量 DATABASE_URL 自动检测数据库类型
# 格式：postgresql://user:pass@host:port/dbname 或留空使用 SQLite
_DATABASE_URL = os.environ.get("DATABASE_URL", "")

if _DATABASE_URL.startswith("postgres"):
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(_DATABASE_URL)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# 数据库连接池（PostgreSQL 时生效）
if _DATABASE_URL.startswith("postgres"):
    DATABASES["default"]["CONN_MAX_AGE"] = 600  # 10 分钟连接复用


# ═══════════════════════════════════════════
# 7. 密码校验
# ═══════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ═══════════════════════════════════════════
# 8. 国际化
# ═══════════════════════════════════════════

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True


# ═══════════════════════════════════════════
# 9. 静态文件（WhiteNoise）
# ═══════════════════════════════════════════

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ═══════════════════════════════════════════
# 10. 默认主键类型
# ═══════════════════════════════════════════

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ═══════════════════════════════════════════
# 11. CORS 配置
# ═══════════════════════════════════════════

# 开发环境：允许所有来源
# 生产环境：通过 CORS_ALLOWED_ORIGINS 限制
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

# 允许的 HTTP 方法
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# 允许携带凭证（Cookie）
CORS_ALLOW_CREDENTIALS = True


# ═══════════════════════════════════════════
# 12. REST Framework 配置
# ═══════════════════════════════════════════

REST_FRAMEWORK = {
    # 默认分页
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # 默认权限
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowOrReadOnly" if not DEBUG else "rest_framework.permissions.AllowAny",
    ],
    # 默认认证
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    # 过滤器后端
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # 异常处理
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # 调试模式下额外启用 Browsable API
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    # 限速（生产环境建议启用）
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# 调试模式：启用 Browsable API
if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "rest_framework.renderers.BrowsableAPIRenderer",
    )
    REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
        "rest_framework.permissions.AllowAny",
    ]
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []


# ═══════════════════════════════════════════
# 13. 日志配置
# ═══════════════════════════════════════════

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s "
                "(%(filename)s:%(lineno)d) %(message)s"
            ),
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}


# ═══════════════════════════════════════════
# 14. 匹配算法参数（业务配置）
# ═══════════════════════════════════════════

MATCH_CONFIG = {
    # 默认匹配权重
    "default_weights": {
        "emotion": 0.50,    # 情绪匹配权重
        "semantic": 0.25,   # 语义匹配权重
        "environment": 0.25,  # 环境适配权重
    },
    # 情绪维度默认值（用于缺失维度）
    "default_emotion_range": {
        "valence": {"min": 3.5, "max": 5.5, "weight": 0.20},
        "arousal": {"min": 3.0, "max": 5.0, "weight": 0.15},
        "warmth": {"min": 3.0, "max": 5.0, "weight": 0.15},
        "tension": {"min": 2.0, "max": 4.0, "weight": 0.10},
        "hope": {"min": 3.5, "max": 5.5, "weight": 0.15},
        "motivation": {"min": 3.0, "max": 5.0, "weight": 0.15},
        "intrusion": {"min": 0.0, "max": 3.0, "weight": 0.10},
    },
    # 风险惩罚系数
    "risk_penalty_coefficient": 0.15,
    # 最低综合匹配阈值（低于此值的推荐将被过滤）
    "min_total_score_threshold": 0.3,
    # 默认返回的推荐数量
    "default_top_k": 10,
    # 侵入感硬上限（超过此值的曲目直接过滤）
    "hard_intrusion_cap": 5.5,
}


# ═══════════════════════════════════════════
# 15. 安全相关（生产环境）
# ═══════════════════════════════════════════

if not DEBUG:
    # HTTPS 安全头
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

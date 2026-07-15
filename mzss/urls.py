"""
URL configuration for mzss project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
]

# 直接 serve 前端构建产物（assets 目录）
urlpatterns += [
    re_path(r"^assets/(?P<path>.*)$", serve, {
        "document_root": settings.BASE_DIR / "frontend" / "dist" / "assets",
    }),
]

# 开发环境：Django 直接 serve 静态文件
# 生产环境：WhiteNoise 处理，不需要这个
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

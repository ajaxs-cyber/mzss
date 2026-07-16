"""
项目级 URL 配置 - 觅知音音乐场景量化匹配系统

所有 API 端点以 /api/ 为前缀挂载。
管理后台保留标准 /admin/ 路径。
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    """
    API 根端点。

    返回系统信息和可用端点列表。
    """
    return JsonResponse({
        "name": "觅知音 - 音乐场景量化匹配系统 API",
        "version": "2.0.0",
        "description": "基于《音乐—场景量化匹配机制技术报告V1.0》",
        "endpoints": {
            "tracks": "/api/tracks/",
            "segments": "/api/segments/",
            "audio_features": "/api/audio-features/",
            "emotion_scores": "/api/emotion-scores/",
            "scene_profiles": "/api/scene-profiles/",
            "recommendations": "/api/recommendations/",
        },
        "admin": "/admin/",
    })


urlpatterns = [
    # 管理后台
    path("admin/", admin.site.urls),

    # API 根
    path("api/", api_root, name="api-root"),

    # 核心应用 API（前缀 /api/）
    path("api/", include("core.urls")),
]

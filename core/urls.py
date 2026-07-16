"""
应用级 URL 路由 - 觅知音音乐场景量化匹配系统

使用 Django REST Framework 的 DefaultRouter 自动注册 ViewSet，
生成标准 RESTful URL 模式。
"""

from rest_framework.routers import DefaultRouter

from .views import (
    TrackViewSet,
    SegmentViewSet,
    AudioFeatureViewSet,
    EmotionScoreViewSet,
    SceneProfileViewSet,
    RecommendationViewSet,
)

# 创建路由器
router = DefaultRouter()

# 注册 ViewSet
# 格式: router.register(prefix, ViewSet, basename)
router.register(r"tracks", TrackViewSet, basename="track")
router.register(r"segments", SegmentViewSet, basename="segment")
router.register(r"audio-features", AudioFeatureViewSet, basename="audio-feature")
router.register(r"emotion-scores", EmotionScoreViewSet, basename="emotion-score")
router.register(r"scene-profiles", SceneProfileViewSet, basename="scene-profile")
router.register(r"recommendations", RecommendationViewSet, basename="recommendation")

# URL 模式
urlpatterns = router.urls

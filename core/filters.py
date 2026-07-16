"""
Django-Filter 过滤器 - 觅知音音乐场景量化匹配系统

为 Track、Segment、AudioFeature、RecommendationLog 提供
高级过滤支持，包括范围过滤、枚举过滤等。
"""

import django_filters
from django.db.models import QuerySet

from .models import Track, Segment, AudioFeature, RecommendationLog


# ═══════════════════════════════════════════
# Track 过滤器
# ═══════════════════════════════════════════

class TrackFilter(django_filters.FilterSet):
    """
    曲目过滤器。

    支持按版权状态、复核状态、人声概率范围、时长范围过滤，
    以及按标题/艺术家模糊搜索。
    """

    # 人声概率范围
    vocal_probability_min = django_filters.NumberFilter(
        field_name="vocal_probability", lookup_expr="gte"
    )
    vocal_probability_max = django_filters.NumberFilter(
        field_name="vocal_probability", lookup_expr="lte"
    )

    # 时长范围（秒）
    duration_min = django_filters.NumberFilter(
        field_name="duration_sec", lookup_expr="gte"
    )
    duration_max = django_filters.NumberFilter(
        field_name="duration_sec", lookup_expr="lte"
    )

    # 标题模糊搜索
    title_contains = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )

    # 艺术家模糊搜索
    artist_contains = django_filters.CharFilter(
        field_name="artist", lookup_expr="icontains"
    )

    class Meta:
        model = Track
        fields = [
            "rights_status",
            "review_status",
            "loopability",
            "commercial_allowed",
        ]


# ═══════════════════════════════════════════
# Segment 过滤器
# ═══════════════════════════════════════════

class SegmentFilter(django_filters.FilterSet):
    """
    片段过滤器。

    支持按曲目 ID、起始/结束时间范围、循环适配性过滤。
    """

    # 按曲目 track_id 过滤
    track_id = django_filters.CharFilter(
        field_name="track__track_id", lookup_expr="exact"
    )

    # 时间段范围
    start_min = django_filters.NumberFilter(
        field_name="start_sec", lookup_expr="gte"
    )
    start_max = django_filters.NumberFilter(
        field_name="start_sec", lookup_expr="lte"
    )
    end_min = django_filters.NumberFilter(
        field_name="end_sec", lookup_expr="gte"
    )
    end_max = django_filters.NumberFilter(
        field_name="end_sec", lookup_expr="lte"
    )

    class Meta:
        model = Segment
        fields = [
            "loopability",
            "fade_in_out",
            "segment_version",
        ]


# ═══════════════════════════════════════════
# AudioFeature 过滤器
# ═══════════════════════════════════════════

class AudioFeatureFilter(django_filters.FilterSet):
    """
    声学特征过滤器。

    支持按 BPM 范围、能量范围、响度范围、频谱质心范围、
    调性概率范围等高级过滤。
    """

    # BPM 范围
    bpm_min = django_filters.NumberFilter(field_name="bpm", lookup_expr="gte")
    bpm_max = django_filters.NumberFilter(field_name="bpm", lookup_expr="lte")

    # 能量范围
    energy_min = django_filters.NumberFilter(field_name="energy", lookup_expr="gte")
    energy_max = django_filters.NumberFilter(field_name="energy", lookup_expr="lte")

    # 响度范围 (LUFS)
    lufs_min = django_filters.NumberFilter(field_name="lufs", lookup_expr="gte")
    lufs_max = django_filters.NumberFilter(field_name="lufs", lookup_expr="lte")

    # 频谱质心范围 (Hz)
    centroid_min = django_filters.NumberFilter(field_name="centroid", lookup_expr="gte")
    centroid_max = django_filters.NumberFilter(field_name="centroid", lookup_expr="lte")

    # 大调概率范围
    major_probability_min = django_filters.NumberFilter(
        field_name="major_probability", lookup_expr="gte"
    )
    major_probability_max = django_filters.NumberFilter(
        field_name="major_probability", lookup_expr="lte"
    )

    # 人声清晰度范围
    vocal_clarity_min = django_filters.NumberFilter(
        field_name="vocal_clarity", lookup_expr="gte"
    )
    vocal_clarity_max = django_filters.NumberFilter(
        field_name="vocal_clarity", lookup_expr="lte"
    )

    # 按曲目 track_id 过滤
    track_id = django_filters.CharFilter(
        field_name="track__track_id", lookup_expr="exact"
    )

    # 动态波动范围
    dynamic_flux_min = django_filters.NumberFilter(
        field_name="dynamic_flux", lookup_expr="gte"
    )
    dynamic_flux_max = django_filters.NumberFilter(
        field_name="dynamic_flux", lookup_expr="lte"
    )

    # 不协和度范围
    dissonance_min = django_filters.NumberFilter(
        field_name="dissonance", lookup_expr="gte"
    )
    dissonance_max = django_filters.NumberFilter(
        field_name="dissonance", lookup_expr="lte"
    )

    class Meta:
        model = AudioFeature
        fields = [
            "extractor_version",
        ]


# ═══════════════════════════════════════════
# Recommendation 过滤器
# ═══════════════════════════════════════════

class RecommendationFilter(django_filters.FilterSet):
    """
    推荐日志过滤器。

    支持按场景画像 ID、总分范围、选中状态、播放状态过滤。
    """

    # 按场景画像 profile_id 过滤
    profile_id = django_filters.CharFilter(
        field_name="profile__profile_id", lookup_expr="exact"
    )

    # 按片段 segment_id 过滤
    segment_id = django_filters.CharFilter(
        field_name="segment__segment_id", lookup_expr="exact"
    )

    # 总分范围
    score_min = django_filters.NumberFilter(
        field_name="total_score", lookup_expr="gte"
    )
    score_max = django_filters.NumberFilter(
        field_name="total_score", lookup_expr="lte"
    )

    # 情绪匹配范围
    emotion_match_min = django_filters.NumberFilter(
        field_name="emotion_match", lookup_expr="gte"
    )

    class Meta:
        model = RecommendationLog
        fields = [
            "selected",
            "played",
        ]

"""
DRF 序列化器 - 觅知音音乐场景量化匹配系统

提供 Track、Segment、AudioFeature、EmotionScore、SceneProfile、
RecommendationLog 的序列化与反序列化支持。

嵌套序列化器设计确保 Track 详情可完整返回 AudioFeature 和 EmotionScore。
"""

from typing import Any, Dict
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import (
    Track,
    Segment,
    AudioFeature,
    EmotionScore,
    SceneProfile,
    RecommendationLog,
)


# ═══════════════════════════════════════════
# AudioFeature 序列化器
# ═══════════════════════════════════════════

class AudioFeatureSerializer(serializers.ModelSerializer):
    """
    声学特征序列化器。

    用于独立查询或嵌套在 Track 详情中。
    所有数值字段均保留完整精度。
    """

    track_id = serializers.CharField(source="track.track_id", read_only=True)
    segment_id = serializers.CharField(
        source="segment.segment_id", read_only=True, default=None
    )

    class Meta:
        model = AudioFeature
        fields = [
            "id",
            "track_id",
            "segment_id",
            # 节奏与速度
            "bpm",
            "beat_cv",
            "onset_rate",
            "percussive_ratio",
            "beat_clarity",
            # 调性与和声
            "major_probability",
            "minor_probability",
            "key_clarity",
            "dissonance",
            "melody_rise",
            # 能量响度动态
            "lufs",
            "lra",
            "spike_count",
            "energy",
            "dynamic_flux",
            # 音色配器
            "centroid",
            "flux",
            "harmonic_ratio",
            "acoustic_probability",
            "electronic_probability",
            "vocal_clarity",
            # 歌词语义
            "lyrics_valence",
            "theme_similarity",
            # 元信息
            "extractor_version",
            "analyzed_at",
        ]


# ═══════════════════════════════════════════
# EmotionScore 序列化器
# ═══════════════════════════════════════════

class EmotionDimensionSerializer(serializers.Serializer):
    """
    单一情绪维度序列化器（用于展示 AI/人工/最终三分值）。
    """

    ai = serializers.FloatField(read_only=True)
    human = serializers.FloatField(read_only=True, allow_null=True)
    final = serializers.FloatField(read_only=True)


class EmotionScoreSerializer(serializers.ModelSerializer):
    """
    情绪评分序列化器。

    提供平铺字段（valence_ai / valence_human / valence_final）
    以及嵌套结构（dimensions.valence.ai / dimensions.valence.human / ...），
    方便前端按需取用。
    """

    track_id = serializers.CharField(source="track.track_id", read_only=True)
    segment_id = serializers.CharField(
        source="segment.segment_id", read_only=True, default=None
    )

    # 嵌套结构：dimensions = {"valence": {"ai": x, "human": y, "final": z}, ...}
    dimensions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmotionScore
        fields = [
            "id",
            "track_id",
            "segment_id",
            # 平铺七维情绪（AI 初判）
            "valence_ai",
            "arousal_ai",
            "warmth_ai",
            "tension_ai",
            "hope_ai",
            "motivation_ai",
            "intrusion_ai",
            # 平铺七维情绪（人工均分）
            "valence_human",
            "arousal_human",
            "warmth_human",
            "tension_human",
            "hope_human",
            "motivation_human",
            "intrusion_human",
            # 平铺七维情绪（最终融合分）
            "valence_final",
            "arousal_final",
            "warmth_final",
            "tension_final",
            "hope_final",
            "motivation_final",
            "intrusion_final",
            # 嵌套结构
            "dimensions",
            # 置信度与融合参数
            "sample_count",
            "agreement_rate",
            "confidence",
            "fusion_lambda",
            "model_version",
            # 时间戳
            "calculated_at",
            "updated_at",
        ]

    def get_dimensions(self, obj: EmotionScore) -> Dict[str, Dict[str, Any]]:
        """组装嵌套情绪维度结构。"""
        dims = {}
        for dim in [
            "valence", "arousal", "warmth", "tension",
            "hope", "motivation", "intrusion",
        ]:
            dims[dim] = {
                "ai": getattr(obj, f"{dim}_ai"),
                "human": getattr(obj, f"{dim}_human"),
                "final": getattr(obj, f"{dim}_final"),
            }
        return dims


# ═══════════════════════════════════════════
# Segment 序列化器
# ═══════════════════════════════════════════

class SegmentSerializer(serializers.ModelSerializer):
    """
    片段序列化器（列表视图用）。

    轻量版本，不包含嵌套的 AudioFeature / EmotionScore。
    """

    track_title = serializers.CharField(source="track.title", read_only=True)
    track_artist = serializers.CharField(source="track.artist", read_only=True)

    class Meta:
        model = Segment
        fields = [
            "id",
            "segment_id",
            "track",
            "track_title",
            "track_artist",
            "start_sec",
            "end_sec",
            "loopability",
            "fade_in_out",
            "segment_version",
        ]


class SegmentDetailSerializer(serializers.ModelSerializer):
    """
    片段详情序列化器。

    包含嵌套的声学特征列表和情绪评分列表。
    """

    track_title = serializers.CharField(source="track.title", read_only=True)
    track_artist = serializers.CharField(source="track.artist", read_only=True)
    audio_features = AudioFeatureSerializer(many=True, read_only=True)
    emotion_scores = EmotionScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Segment
        fields = [
            "id",
            "segment_id",
            "track",
            "track_title",
            "track_artist",
            "start_sec",
            "end_sec",
            "loopability",
            "fade_in_out",
            "segment_version",
            "audio_features",
            "emotion_scores",
        ]


class SegmentNestedSerializer(serializers.ModelSerializer):
    """
    片段嵌套序列化器（用于 Track 详情中嵌入片段列表）。

    轻量版本，避免循环引用。
    """

    class Meta:
        model = Segment
        fields = [
            "id",
            "segment_id",
            "start_sec",
            "end_sec",
            "loopability",
            "fade_in_out",
            "segment_version",
        ]


# ═══════════════════════════════════════════
# Track 序列化器
# ═══════════════════════════════════════════

class TrackListSerializer(serializers.ModelSerializer):
    """
    曲目列表序列化器（轻量）。

    用于 /api/tracks/ 列表查询，不包含嵌套详情。
    """

    class Meta:
        model = Track
        fields = [
            "id",
            "track_id",
            "title",
            "artist",
            "rights_status",
            "duration_sec",
            "vocal_probability",
            "commercial_allowed",
            "review_status",
            "loopability",
            "cover_image",
            "created_at",
        ]


class TrackDetailSerializer(serializers.ModelSerializer):
    """
    曲目详情序列化器（完整）。

    用于 /api/tracks/{id}/ 详情查询，
    完整返回 AudioFeature、EmotionScore 和 Segment 列表。
    """

    audio_features = AudioFeatureSerializer(read_only=True)
    emotion_score = EmotionScoreSerializer(read_only=True)
    segments = SegmentNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = [
            "id",
            "track_id",
            "title",
            "artist",
            "rights_status",
            "duration_sec",
            "vocal_probability",
            "lyrics_language",
            "commercial_allowed",
            "review_status",
            "loopability",
            "audio_file_url",
            "cover_image",
            # 嵌套详情
            "audio_features",
            "emotion_score",
            "segments",
            # 时间戳
            "created_at",
            "updated_at",
        ]


class TrackCreateUpdateSerializer(serializers.ModelSerializer):
    """
    曲目创建/更新序列化器。

    用于 POST / PATCH 请求，不包含嵌套只读字段。
    """

    class Meta:
        model = Track
        fields = [
            "track_id",
            "title",
            "artist",
            "rights_status",
            "duration_sec",
            "vocal_probability",
            "lyrics_language",
            "commercial_allowed",
            "review_status",
            "loopability",
            "audio_file_url",
            "cover_image",
        ]


# ═══════════════════════════════════════════
# SceneProfile 序列化器
# ═══════════════════════════════════════════

class SceneProfileSerializer(serializers.ModelSerializer):
    """
    场景画像序列化器。

    支持完整的 CRUD 操作，target_emotion 以原始 JSON 透传。
    """

    class Meta:
        model = SceneProfile
        fields = [
            "id",
            "profile_id",
            "scene_name",
            "industry",
            "topic_keywords",
            # 目标用户
            "target_user_age",
            "target_user_language",
            "target_user_device",
            # 当前任务
            "current_task",
            # 品牌感受
            "brand_keywords",
            # 目标情绪区间
            "target_emotion",
            # 视觉风格
            "visual_style",
            # 播放策略
            "playback_position",
            "autoplay",
            "loop",
            # 约束
            "lyrics_allowed",
            "vocal_allowed",
            "preferred_bpm_range",
            "max_intrusion_risk",
            "environment",
            # 状态
            "confirmed",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_target_emotion(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """
        校验 target_emotion JSON 结构完整性。
        """
        required_dims = [
            "valence", "arousal", "warmth", "tension",
            "hope", "motivation", "intrusion",
        ]
        if not isinstance(value, dict):
            raise serializers.ValidationError("target_emotion 必须是 JSON 对象。")

        for dim in required_dims:
            if dim not in value:
                raise serializers.ValidationError(
                    f"target_emotion 缺少必需维度 '{dim}'。"
                )
            cfg = value[dim]
            for key in ("min", "max", "weight"):
                if key not in cfg:
                    raise serializers.ValidationError(
                        f"target_emotion.{dim} 缺少 '{key}' 字段。"
                    )
            if not (0.0 <= cfg["min"] <= 7.0 and 0.0 <= cfg["max"] <= 7.0):
                raise serializers.ValidationError(
                    f"target_emotion.{dim} 的 min/max 必须在 0-7 范围内。"
                )
            if cfg["min"] > cfg["max"]:
                raise serializers.ValidationError(
                    f"target_emotion.{dim} 的 min 不能大于 max。"
                )
            if not (0.0 <= cfg["weight"] <= 1.0):
                raise serializers.ValidationError(
                    f"target_emotion.{dim} 的 weight 必须在 0-1 范围内。"
                )
        return value


# ═══════════════════════════════════════════
# RecommendationLog 序列化器
# ═══════════════════════════════════════════

class RecommendationLogSerializer(serializers.ModelSerializer):
    """
    推荐日志序列化器（列表/详情）。

    嵌套展示关联的场景画像和片段信息。
    """

    profile_id = serializers.CharField(
        source="profile.profile_id", read_only=True
    )
    scene_name = serializers.CharField(
        source="profile.scene_name", read_only=True
    )
    segment_id = serializers.CharField(
        source="segment.segment_id", read_only=True
    )
    track_title = serializers.CharField(
        source="segment.track.title", read_only=True
    )
    track_artist = serializers.CharField(
        source="segment.track.artist", read_only=True
    )

    class Meta:
        model = RecommendationLog
        fields = [
            "id",
            "profile",
            "profile_id",
            "scene_name",
            "segment",
            "segment_id",
            "track_title",
            "track_artist",
            # 匹配分数
            "emotion_match",
            "semantic_match",
            "environment_fit",
            "risk_penalty",
            "total_score",
            # 状态
            "filter_reason",
            "selected",
            "played",
            "created_at",
        ]


class RecommendationCreateSerializer(serializers.ModelSerializer):
    """
    推荐日志创建序列化器。

    仅允许写入外键和分数字段，状态字段由业务逻辑控制。
    """

    class Meta:
        model = RecommendationLog
        fields = [
            "profile",
            "segment",
            "emotion_match",
            "semantic_match",
            "environment_fit",
            "risk_penalty",
            "total_score",
        ]


# ═══════════════════════════════════════════
# 场景匹配结果序列化器（非模型序列化器）
# ═══════════════════════════════════════════

class MatchResultSerializer(serializers.Serializer):
    """
    场景匹配结果序列化器。

    用于 /api/scene-profiles/{id}/match/ 接口返回，
    不是模型序列化器，而是业务计算结果的包装。
    """

    segment_id = serializers.CharField(read_only=True)
    track_id = serializers.CharField(read_only=True)
    track_title = serializers.CharField(read_only=True)
    track_artist = serializers.CharField(read_only=True)

    # 各维度分数
    emotion_match = serializers.FloatField(read_only=True)
    semantic_match = serializers.FloatField(read_only=True)
    environment_fit = serializers.FloatField(read_only=True)
    risk_penalty = serializers.FloatField(read_only=True)
    total_score = serializers.FloatField(read_only=True)

    # 情绪明细
    emotion_details = serializers.DictField(read_only=True, child=serializers.FloatField())

    # 过滤信息
    filter_reason = serializers.CharField(read_only=True, allow_blank=True)
    passed = serializers.BooleanField(read_only=True)

    # 建议播放策略
    loopability_advice = serializers.CharField(read_only=True)
    fade_in_out_advice = serializers.BooleanField(read_only=True)

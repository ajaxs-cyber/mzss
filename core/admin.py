"""
Django 管理后台配置 - 觅知音音乐场景量化匹配系统

为六大核心模型注册管理界面，优化列表展示、搜索和过滤。
"""

from django.contrib import admin

from .models import (
    Track,
    Segment,
    AudioFeature,
    EmotionScore,
    SceneProfile,
    RecommendationLog,
)


# ═══════════════════════════════════════════
# 1. Track 管理
# ═══════════════════════════════════════════

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """曲目管理后台配置。"""

    list_display = [
        "track_id",
        "title",
        "artist",
        "rights_status",
        "review_status",
        "duration_sec",
        "vocal_probability",
        "commercial_allowed",
        "loopability",
        "created_at",
    ]
    list_filter = [
        "rights_status",
        "review_status",
        "loopability",
        "commercial_allowed",
        "created_at",
    ]
    search_fields = ["track_id", "title", "artist"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("基础元数据", {
            "fields": (
                "track_id", "title", "artist",
                "duration_sec", "vocal_probability", "lyrics_language",
            ),
        }),
        ("版权与状态", {
            "fields": (
                "rights_status", "commercial_allowed", "review_status",
            ),
        }),
        ("播放配置", {
            "fields": ("loopability", "audio_file_url", "cover_image"),
        }),
        ("时间戳", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ["created_at", "updated_at"]


# ═══════════════════════════════════════════
# 2. Segment 管理（内联到 Track）
# ═══════════════════════════════════════════

class SegmentInline(admin.TabularInline):
    """Track 详情页内联展示 Segment。"""

    model = Segment
    extra = 0
    fields = ["segment_id", "start_sec", "end_sec", "loopability", "fade_in_out", "segment_version"]
    ordering = ["start_sec"]


# 重新注册 TrackAdmin，加入内联
admin.site.unregister(Track)


@admin.register(Track)
class TrackAdminWithInline(admin.ModelAdmin):
    """曲目管理后台配置（含片段内联）。"""

    list_display = [
        "track_id",
        "title",
        "artist",
        "rights_status",
        "review_status",
        "duration_sec",
        "vocal_probability",
        "commercial_allowed",
        "loopability",
        "created_at",
    ]
    list_filter = [
        "rights_status",
        "review_status",
        "loopability",
        "commercial_allowed",
        "created_at",
    ]
    search_fields = ["track_id", "title", "artist"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    inlines = [SegmentInline]

    fieldsets = (
        ("基础元数据", {
            "fields": (
                "track_id", "title", "artist",
                "duration_sec", "vocal_probability", "lyrics_language",
            ),
        }),
        ("版权与状态", {
            "fields": (
                "rights_status", "commercial_allowed", "review_status",
            ),
        }),
        ("播放配置", {
            "fields": ("loopability", "audio_file_url", "cover_image"),
        }),
        ("时间戳", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    """片段管理后台配置。"""

    list_display = [
        "segment_id",
        "track",
        "start_sec",
        "end_sec",
        "loopability",
        "fade_in_out",
        "segment_version",
    ]
    list_filter = ["loopability", "fade_in_out", "segment_version"]
    search_fields = ["segment_id", "track__title", "track__artist"]
    ordering = ["track", "start_sec"]
    autocomplete_fields = ["track"]


# ═══════════════════════════════════════════
# 3. AudioFeature 管理
# ═══════════════════════════════════════════

@admin.register(AudioFeature)
class AudioFeatureAdmin(admin.ModelAdmin):
    """声学特征管理后台配置。"""

    list_display = [
        "id",
        "track",
        "segment",
        "bpm",
        "energy",
        "lufs",
        "centroid",
        "major_probability",
        "vocal_clarity",
        "analyzed_at",
    ]
    list_filter = ["extractor_version", "analyzed_at"]
    search_fields = ["track__track_id", "track__title", "segment__segment_id"]
    ordering = ["-analyzed_at"]
    date_hierarchy = "analyzed_at"

    fieldsets = (
        ("关联", {
            "fields": ("track", "segment"),
        }),
        ("节奏与速度", {
            "fields": ("bpm", "beat_cv", "onset_rate", "percussive_ratio", "beat_clarity"),
            "classes": ("collapse",),
        }),
        ("调性与和声", {
            "fields": ("major_probability", "minor_probability", "key_clarity", "dissonance", "melody_rise"),
            "classes": ("collapse",),
        }),
        ("能量响度动态", {
            "fields": ("lufs", "lra", "spike_count", "energy", "dynamic_flux"),
            "classes": ("collapse",),
        }),
        ("音色配器", {
            "fields": ("centroid", "flux", "harmonic_ratio", "acoustic_probability", "electronic_probability", "vocal_clarity"),
            "classes": ("collapse",),
        }),
        ("歌词语义", {
            "fields": ("lyrics_valence", "theme_similarity"),
            "classes": ("collapse",),
        }),
        ("元信息", {
            "fields": ("extractor_version", "analyzed_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ["analyzed_at"]


# ═══════════════════════════════════════════
# 4. EmotionScore 管理
# ═══════════════════════════════════════════

@admin.register(EmotionScore)
class EmotionScoreAdmin(admin.ModelAdmin):
    """情绪评分管理后台配置。"""

    list_display = [
        "id",
        "track",
        "segment",
        "valence_final",
        "arousal_final",
        "warmth_final",
        "tension_final",
        "hope_final",
        "motivation_final",
        "intrusion_final",
        "confidence",
        "sample_count",
        "calculated_at",
    ]
    list_filter = ["model_version", "sample_count", "calculated_at"]
    search_fields = ["track__track_id", "track__title", "segment__segment_id"]
    ordering = ["-calculated_at"]
    date_hierarchy = "calculated_at"

    fieldsets = (
        ("关联", {
            "fields": ("track", "segment"),
        }),
        ("效价 (Valence)", {
            "fields": ("valence_ai", "valence_human", "valence_final"),
            "classes": ("collapse",),
        }),
        ("唤醒度 (Arousal)", {
            "fields": ("arousal_ai", "arousal_human", "arousal_final"),
            "classes": ("collapse",),
        }),
        ("温暖度 (Warmth)", {
            "fields": ("warmth_ai", "warmth_human", "warmth_final"),
            "classes": ("collapse",),
        }),
        ("紧张度 (Tension)", {
            "fields": ("tension_ai", "tension_human", "tension_final"),
            "classes": ("collapse",),
        }),
        ("希望感 (Hope)", {
            "fields": ("hope_ai", "hope_human", "hope_final"),
            "classes": ("collapse",),
        }),
        ("动力感 (Motivation)", {
            "fields": ("motivation_ai", "motivation_human", "motivation_final"),
            "classes": ("collapse",),
        }),
        ("侵入感 (Intrusion)", {
            "fields": ("intrusion_ai", "intrusion_human", "intrusion_final"),
            "classes": ("collapse",),
        }),
        ("置信度与融合参数", {
            "fields": ("sample_count", "agreement_rate", "confidence", "fusion_lambda", "model_version"),
        }),
        ("时间戳", {
            "fields": ("calculated_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ["calculated_at", "updated_at"]


# ═══════════════════════════════════════════
# 5. SceneProfile 管理
# ═══════════════════════════════════════════

@admin.register(SceneProfile)
class SceneProfileAdmin(admin.ModelAdmin):
    """场景画像管理后台配置。"""

    list_display = [
        "profile_id",
        "scene_name",
        "industry",
        "current_task",
        "confirmed",
        "environment",
        "created_at",
    ]
    list_filter = [
        "industry",
        "current_task",
        "confirmed",
        "environment",
        "created_at",
    ]
    search_fields = ["profile_id", "scene_name", "topic_keywords"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("基础信息", {
            "fields": ("profile_id", "scene_name", "industry", "topic_keywords"),
        }),
        ("目标用户", {
            "fields": ("target_user_age", "target_user_language", "target_user_device"),
        }),
        ("品牌感受与任务", {
            "fields": ("current_task", "brand_keywords"),
        }),
        ("目标情绪区间", {
            "fields": ("target_emotion",),
            "description": "JSON 格式：{valence: {min, max, weight}, ...}",
        }),
        ("视觉风格", {
            "fields": ("visual_style",),
            "classes": ("collapse",),
        }),
        ("播放策略", {
            "fields": ("playback_position", "autoplay", "loop"),
        }),
        ("约束条件", {
            "fields": (
                "lyrics_allowed", "vocal_allowed",
                "preferred_bpm_range", "max_intrusion_risk", "environment",
            ),
        }),
        ("状态", {
            "fields": ("confirmed", "created_at"),
        }),
    )
    readonly_fields = ["created_at"]


# ═══════════════════════════════════════════
# 6. RecommendationLog 管理
# ═══════════════════════════════════════════

@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    """推荐日志管理后台配置。"""

    list_display = [
        "id",
        "profile",
        "segment",
        "total_score",
        "emotion_match",
        "semantic_match",
        "environment_fit",
        "risk_penalty",
        "selected",
        "played",
        "created_at",
    ]
    list_filter = [
        "selected",
        "played",
        "created_at",
    ]
    search_fields = [
        "profile__profile_id",
        "segment__segment_id",
        "segment__track__title",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("关联", {
            "fields": ("profile", "segment"),
        }),
        ("匹配分数", {
            "fields": (
                "emotion_match", "semantic_match",
                "environment_fit", "risk_penalty", "total_score",
            ),
        }),
        ("状态", {
            "fields": ("filter_reason", "selected", "played"),
        }),
        ("时间戳", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ["created_at"]

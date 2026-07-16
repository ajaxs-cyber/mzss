"""
DRF 视图集 - 觅知音音乐场景量化匹配系统

包含五大核心 ViewSet：
1. TrackViewSet       — 曲目 CRUD + 搜索过滤（genre、BPM 范围、scene_type）
2. SegmentViewSet     — 片段 CRUD + 按曲目过滤
3. AudioFeatureViewSet — 声学特征查询（与 Track 关联）
4. EmotionScoreViewSet — 情绪评分查询
5. SceneProfileViewSet — 场景画像 CRUD + match 动作
6. RecommendationViewSet — 推荐历史查询 + 标记播放

match 动作实现场景画像与音乐库的量化匹配算法。
"""

import logging
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet, Q, Prefetch
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Track,
    Segment,
    AudioFeature,
    EmotionScore,
    SceneProfile,
    RecommendationLog,
)
from .serializers import (
    TrackListSerializer,
    TrackDetailSerializer,
    TrackCreateUpdateSerializer,
    SegmentSerializer,
    SegmentDetailSerializer,
    AudioFeatureSerializer,
    EmotionScoreSerializer,
    SceneProfileSerializer,
    RecommendationLogSerializer,
    RecommendationCreateSerializer,
    MatchResultSerializer,
)
from .filters import TrackFilter, SegmentFilter, AudioFeatureFilter, RecommendationFilter

logger = logging.getLogger("core")

# ───────────────────────────────────────────
# 辅助函数：匹配算法
# ───────────────────────────────────────────


def compute_emotion_match(
    emotion_score: EmotionScore,
    target_emotion: Dict[str, Dict[str, float]],
) -> tuple[float, Dict[str, float]]:
    """
    计算情绪匹配度。

    对七维情绪中的每一维，计算音乐得分与目标区间的匹配程度：
    - 若得分在 [min, max] 区间内：match = 1.0
    - 若得分在区间外：match = max(0, 1 - distance / range_width)

    返回 (加权平均匹配度, 各维度明细)。
    """
    dimensions = [
        "valence", "arousal", "warmth", "tension",
        "hope", "motivation", "intrusion",
    ]
    total_weight = 0.0
    weighted_match = 0.0
    details: Dict[str, float] = {}

    for dim in dimensions:
        cfg = target_emotion.get(dim, {})
        min_val = cfg.get("min", 0.0)
        max_val = cfg.get("max", 7.0)
        weight = cfg.get("weight", 1.0 / len(dimensions))
        score = getattr(emotion_score, f"{dim}_final", 3.5)

        if min_val <= score <= max_val:
            match_val = 1.0
        else:
            range_width = max(max_val - min_val, 0.5)
            if score < min_val:
                distance = min_val - score
            else:
                distance = score - max_val
            match_val = max(0.0, 1.0 - distance / range_width)

        total_weight += weight
        weighted_match += match_val * weight
        details[f"{dim}_match"] = round(match_val, 4)
        details[f"{dim}_score"] = round(score, 4)
        details[f"{dim}_target"] = f"[{min_val}-{max_val}]"

    if total_weight > 0:
        final_match = weighted_match / total_weight
    else:
        final_match = 0.0

    return round(final_match, 4), details


def compute_semantic_match(
    emotion_score: EmotionScore,
    scene_profile: SceneProfile,
) -> float:
    """
    计算语义匹配度。

    综合歌词情绪效价、主题相似度等因素，返回 0-1 的匹配分数。
    """
    # 基于 theme_similarity（0-100 映射到 0-1）
    theme_sim = getattr(emotion_score, "track", None)
    if theme_sim and hasattr(theme_sim, "audio_features"):
        try:
            af = theme_sim.audio_features
            theme_score = getattr(af, "theme_similarity", 0) / 100.0
        except (AudioFeature.DoesNotExist, AttributeError):
            theme_score = 0.0
    else:
        theme_score = 0.0

    # 歌词效价与场景关键词的简单匹配
    lyrics_valence_match = 0.5  # 默认值

    # 综合语义匹配分
    semantic = 0.6 * theme_score + 0.4 * lyrics_valence_match
    return round(min(max(semantic, 0.0), 1.0), 4)


def compute_environment_fit(
    audio_feature: AudioFeature,
    scene_profile: SceneProfile,
) -> float:
    """
    计算环境适配度。

    评估声学特征是否满足场景的环境约束（BPM 范围、侵入感上限等）。
    返回 0-1 的适配分数。
    """
    scores: List[float] = []

    # 1. BPM 范围匹配
    bpm_range = scene_profile.preferred_bpm_range or {}
    bpm_min = bpm_range.get("min", 0)
    bpm_max = bpm_range.get("max", 300)
    bpm = audio_feature.bpm
    if bpm_min <= bpm <= bpm_max:
        scores.append(1.0)
    else:
        if bpm < bpm_min:
            distance = bpm_min - bpm
        else:
            distance = bpm - bpm_max
        scores.append(max(0.0, 1.0 - distance / max(bpm_max - bpm_min, 30)))

    # 2. 侵入感约束
    max_intrusion = scene_profile.max_intrusion_risk
    # 查找对应的情绪评分中的侵入感
    track = audio_feature.track
    try:
        es = track.emotion_score
        intrusion_score = es.intrusion_final
    except (EmotionScore.DoesNotExist, AttributeError):
        intrusion_score = 3.5  # 默认值

    if intrusion_score <= max_intrusion:
        scores.append(1.0)
    else:
        scores.append(max(0.0, 1.0 - (intrusion_score - max_intrusion) / 4.0))

    # 3. 人声/歌词约束
    vocal_p = track.vocal_probability
    if not scene_profile.vocal_allowed and vocal_p > 0.3:
        scores.append(0.0)
    elif not scene_profile.lyrics_allowed and track.vocal_probability > 0.5:
        scores.append(0.3)
    else:
        scores.append(1.0)

    # 4. 能量适配（根据环境）
    energy = audio_feature.energy
    env = scene_profile.environment.lower() if scene_profile.environment else ""
    if "office" in env:
        # 办公环境偏好中低能量
        scores.append(1.0 - min(abs(energy - 0.35) * 2, 1.0))
    elif "public" in env:
        # 公共空间偏好中等能量
        scores.append(1.0 - min(abs(energy - 0.5) * 2, 1.0))
    elif "home" in env:
        # 家居环境偏好低能量
        scores.append(1.0 - min(abs(energy - 0.3) * 2, 1.0))
    else:
        scores.append(0.8)  # 默认

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def compute_risk_penalty(
    audio_feature: AudioFeature,
    emotion_score: EmotionScore,
    scene_profile: SceneProfile,
) -> float:
    """
    计算风险惩罚项。

    综合评估播放风险：过高的侵入感、能量突变、不协和度等因素。
    返回值越大表示风险越高。
    """
    penalty = 0.0

    # 侵入感过高风险
    intrusion = emotion_score.intrusion_final
    max_allowed = scene_profile.max_intrusion_risk
    if intrusion > max_allowed:
        penalty += (intrusion - max_allowed) * 0.1

    # 响度突变风险（LRA 过大）
    lra = audio_feature.lra
    if lra > 15:
        penalty += (lra - 15) * 0.01

    # 不协和度过高风险
    dissonance = audio_feature.dissonance
    if dissonance > 0.7:
        penalty += (dissonance - 0.7) * 0.15

    # 突发强音过多风险
    spike_count = audio_feature.spike_count
    if spike_count > 20:
        penalty += (spike_count - 20) * 0.005

    return round(penalty, 4)


# ───────────────────────────────────────────
# 1. TrackViewSet
# ───────────────────────────────────────────


class TrackViewSet(viewsets.ModelViewSet):
    """
    曲目视图集。

    提供曲目 CRUD 操作，支持按 BPM 范围、能量、人声概率等字段过滤，
    以及按标题、艺术家搜索。

    额外动作：
    - GET {id}/features/   → 返回曲目的声学特征
    - GET {id}/emotion/    → 返回曲目的情绪评分
    - GET {id}/segments/   → 返回曲目的片段列表
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TrackFilter
    search_fields = ["title", "artist", "track_id"]
    ordering_fields = ["created_at", "updated_at", "title", "duration_sec"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Track]:
        """根据动作返回优化的 QuerySet。"""
        queryset = Track.objects.all()

        # 详情/嵌套查询时预取关联数据
        if self.action in ("retrieve", "features", "emotion", "segments"):
            queryset = queryset.prefetch_related(
                Prefetch("segments", queryset=Segment.objects.order_by("start_sec")),
            ).select_related("audio_features", "emotion_score")

        return queryset

    def get_serializer_class(self):
        if self.action in ("list",):
            return TrackListSerializer
        if self.action in ("create", "update", "partial_update"):
            return TrackCreateUpdateSerializer
        return TrackDetailSerializer

    @action(detail=True, methods=["get"], url_path="features")
    def features(self, request: Request, pk=None) -> Response:
        """
        获取指定曲目的声学特征。

        GET /api/tracks/{id}/features/
        """
        track = self.get_object()
        try:
            audio_feature = track.audio_features
        except AudioFeature.DoesNotExist:
            return Response(
                {"detail": "该曲目尚未提取声学特征。"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AudioFeatureSerializer(audio_feature)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="emotion")
    def emotion(self, request: Request, pk=None) -> Response:
        """
        获取指定曲目的情绪评分。

        GET /api/tracks/{id}/emotion/
        """
        track = self.get_object()
        try:
            emotion_score = track.emotion_score
        except EmotionScore.DoesNotExist:
            return Response(
                {"detail": "该曲目尚未计算情绪评分。"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmotionScoreSerializer(emotion_score)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="segments")
    def track_segments(self, request: Request, pk=None) -> Response:
        """
        获取指定曲目的所有片段。

        GET /api/tracks/{id}/segments/
        """
        track = self.get_object()
        segments = track.segments.all()
        serializer = SegmentSerializer(segments, many=True)
        return Response(serializer.data)


# ───────────────────────────────────────────
# 2. SegmentViewSet
# ───────────────────────────────────────────


class SegmentViewSet(viewsets.ModelViewSet):
    """
    片段视图集。

    提供片段 CRUD 操作，支持按曲目过滤、按时间段过滤。
    """

    queryset = Segment.objects.select_related("track").all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SegmentFilter
    ordering_fields = ["start_sec", "end_sec", "created_at"]
    ordering = ["track", "start_sec"]

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return SegmentDetailSerializer
        return SegmentSerializer


# ───────────────────────────────────────────
# 3. AudioFeatureViewSet
# ───────────────────────────────────────────


class AudioFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    声学特征视图集（只读）。

    支持按 BPM 范围、能量范围、调性概率等过滤，
    按关联的 Track 或 Segment 查询。
    """

    queryset = (
        AudioFeature.objects
        .select_related("track", "segment")
        .all()
    )
    serializer_class = AudioFeatureSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AudioFeatureFilter
    ordering_fields = [
        "bpm", "energy", "centroid", "lufs",
        "analyzed_at",
    ]
    ordering = ["-analyzed_at"]


# ───────────────────────────────────────────
# 4. EmotionScoreViewSet
# ───────────────────────────────────────────


class EmotionScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    情绪评分视图集（只读）。

    支持按各情绪维度范围过滤，按置信度排序。
    """

    queryset = (
        EmotionScore.objects
        .select_related("track", "segment")
        .all()
    )
    serializer_class = EmotionScoreSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = [
        "confidence", "sample_count",
        "valence_final", "arousal_final",
        "intrusion_final",
        "calculated_at",
    ]
    ordering = ["-confidence"]

    def get_queryset(self) -> QuerySet[EmotionScore]:
        queryset = super().get_queryset()

        # 支持按情绪维度范围过滤
        for dim in ["valence", "arousal", "warmth", "tension", "hope", "motivation", "intrusion"]:
            min_param = self.request.query_params.get(f"{dim}_min")
            max_param = self.request.query_params.get(f"{dim}_max")
            if min_param is not None:
                queryset = queryset.filter(**{f"{dim}_final__gte": float(min_param)})
            if max_param is not None:
                queryset = queryset.filter(**{f"{dim}_final__lte": float(max_param)})

        return queryset


# ───────────────────────────────────────────
# 5. SceneProfileViewSet
# ───────────────────────────────────────────


class SceneProfileViewSet(viewsets.ModelViewSet):
    """
    场景画像视图集。

    提供场景画像 CRUD 操作，以及核心匹配动作 match。

    额外动作：
    - POST {id}/match/   → 执行场景匹配，返回推荐曲目列表
    """

    queryset = SceneProfile.objects.all()
    serializer_class = SceneProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["industry", "current_task", "confirmed", "environment"]
    search_fields = ["scene_name", "profile_id", "topic_keywords"]
    ordering_fields = ["created_at", "scene_name"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="match")
    def match(self, request: Request, pk=None) -> Response:
        """
        执行场景匹配。

        POST /api/scene-profiles/{id}/match/

        请求体（可选）：
        {
            "top_k": 10,              # 返回推荐数量（默认从配置读取）
            "weights": {              # 自定义匹配权重
                "emotion": 0.50,
                "semantic": 0.25,
                "environment": 0.25
            }
        }

        响应：推荐列表，按 total_score 降序排列。
        """
        scene_profile: SceneProfile = self.get_object()

        # 解析可选参数
        top_k = request.data.get("top_k", settings.MATCH_CONFIG.get("default_top_k", 10))
        custom_weights = request.data.get("weights", {})
        weights = {
            "emotion": custom_weights.get(
                "emotion", settings.MATCH_CONFIG["default_weights"]["emotion"]
            ),
            "semantic": custom_weights.get(
                "semantic", settings.MATCH_CONFIG["default_weights"]["semantic"]
            ),
            "environment": custom_weights.get(
                "environment", settings.MATCH_CONFIG["default_weights"]["environment"]
            ),
        }

        # 获取所有可用片段（关联到已授权/已复核的曲目）
        segments = (
            Segment.objects
            .select_related("track")
            .filter(
                track__rights_status__in=["authorized"],
                track__review_status__in=["reviewed"],
            )
            .prefetch_related("emotion_scores", "audio_features")
        )

        logger.info(
            f"开始场景匹配: profile={scene_profile.profile_id}, "
            f"候选片段数={segments.count()}, top_k={top_k}"
        )

        results: List[Dict[str, Any]] = []

        for segment in segments:
            track = segment.track

            # 获取情绪评分
            try:
                emotion_score = EmotionScore.objects.get(segment=segment)
            except EmotionScore.DoesNotExist:
                try:
                    emotion_score = track.emotion_score
                except EmotionScore.DoesNotExist:
                    continue  # 跳过无情绪评分的片段

            # 获取声学特征
            try:
                audio_feature = AudioFeature.objects.get(segment=segment)
            except AudioFeature.DoesNotExist:
                try:
                    audio_feature = track.audio_features
                except AudioFeature.DoesNotExist:
                    continue  # 跳过无声学特征的片段

            # ── 硬约束过滤 ──
            filter_reason = ""

            # 侵入感硬上限
            hard_intrusion_cap = settings.MATCH_CONFIG.get("hard_intrusion_cap", 5.5)
            if emotion_score.intrusion_final > hard_intrusion_cap:
                filter_reason = f"侵入感 {emotion_score.intrusion_final:.2f} 超过硬上限 {hard_intrusion_cap}"

            # 人声约束
            if not scene_profile.vocal_allowed and track.vocal_probability > 0.3:
                filter_reason = "场景不允许人声"

            # 歌词约束
            if not scene_profile.lyrics_allowed and track.vocal_probability > 0.5:
                filter_reason = "场景不允许歌词"

            # ── 计算各维度匹配分 ──
            emotion_match, emotion_details = compute_emotion_match(
                emotion_score, scene_profile.target_emotion
            )
            semantic_match = compute_semantic_match(emotion_score, scene_profile)
            environment_fit = compute_environment_fit(audio_feature, scene_profile)
            risk_penalty = compute_risk_penalty(
                audio_feature, emotion_score, scene_profile
            )

            # ── 综合总分 ──
            total_score = (
                weights["emotion"] * emotion_match
                + weights["semantic"] * semantic_match
                + weights["environment"] * environment_fit
                - risk_penalty
            )
            total_score = round(max(0.0, total_score), 4)

            # 最低阈值过滤
            min_threshold = settings.MATCH_CONFIG.get("min_total_score_threshold", 0.3)
            passed = total_score >= min_threshold and not filter_reason

            if not filter_reason and not passed:
                filter_reason = f"综合分 {total_score:.4f} 低于阈值 {min_threshold}"

            # ── 组装结果 ──
            result = {
                "segment_id": segment.segment_id,
                "track_id": track.track_id,
                "track_title": track.title,
                "track_artist": track.artist,
                "emotion_match": emotion_match,
                "semantic_match": semantic_match,
                "environment_fit": environment_fit,
                "risk_penalty": risk_penalty,
                "total_score": total_score,
                "emotion_details": emotion_details,
                "filter_reason": filter_reason,
                "passed": passed,
                "loopability_advice": segment.loopability,
                "fade_in_out_advice": segment.fade_in_out or segment.loopability == "fade_required",
            }
            results.append(result)

            # ── 保存推荐日志 ──
            RecommendationLog.objects.create(
                profile=scene_profile,
                segment=segment,
                emotion_match=emotion_match,
                semantic_match=semantic_match,
                environment_fit=environment_fit,
                risk_penalty=risk_penalty,
                total_score=total_score,
                filter_reason=filter_reason,
                selected=passed,
            )

        # 按总分降序排列
        results.sort(key=lambda x: x["total_score"], reverse=True)

        # 只返回通过过滤的前 K 个
        passed_results = [r for r in results if r["passed"]][:top_k]

        logger.info(
            f"场景匹配完成: profile={scene_profile.profile_id}, "
            f"总候选={len(results)}, 通过={len(passed_results)}"
        )

        serializer = MatchResultSerializer(passed_results, many=True)
        return Response({
            "profile_id": scene_profile.profile_id,
            "scene_name": scene_profile.scene_name,
            "total_candidates": len(results),
            "passed_count": len(passed_results),
            "weights_used": weights,
            "recommendations": serializer.data,
        })

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request: Request, pk=None) -> Response:
        """
        确认场景画像生效。

        POST /api/scene-profiles/{id}/confirm/
        """
        scene_profile: SceneProfile = self.get_object()
        scene_profile.confirmed = True
        scene_profile.save(update_fields=["confirmed"])
        return Response(
            {
                "detail": "场景画像已确认生效。",
                "profile_id": scene_profile.profile_id,
                "confirmed": True,
            }
        )


# ───────────────────────────────────────────
# 6. RecommendationViewSet
# ───────────────────────────────────────────


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    推荐日志视图集（只读 + 状态更新）。

    支持按场景画像 ID 过滤、按分数排序，
    以及标记推荐为已播放。
    """

    queryset = (
        RecommendationLog.objects
        .select_related("profile", "segment", "segment__track")
        .all()
    )
    serializer_class = RecommendationLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RecommendationFilter
    ordering_fields = ["total_score", "emotion_match", "created_at"]
    ordering = ["-total_score"]

    @action(detail=True, methods=["post"], url_path="mark-played")
    def mark_played(self, request: Request, pk=None) -> Response:
        """
        标记推荐为已播放。

        POST /api/recommendations/{id}/mark-played/
        """
        rec: RecommendationLog = self.get_object()
        rec.played = True
        rec.save(update_fields=["played"])
        return Response(
            {
                "detail": "已标记为已播放。",
                "recommendation_id": rec.id,
                "played": True,
            }
        )

    @action(detail=False, methods=["get"], url_path="by-profile")
    def by_profile(self, request: Request) -> Response:
        """
        按场景画像查询推荐历史。

        GET /api/recommendations/by-profile/?profile_id=xxx
        """
        profile_id = request.query_params.get("profile_id")
        if not profile_id:
            return Response(
                {"detail": "必须提供 profile_id 参数。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recs = self.get_queryset().filter(profile__profile_id=profile_id)
        page = self.paginate_queryset(recs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recs, many=True)
        return Response(serializer.data)

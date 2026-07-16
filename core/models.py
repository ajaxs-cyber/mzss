"""
核心数据模型 - 觅知音音乐场景量化匹配系统

基于《音乐—场景量化匹配机制技术报告V1.0》设计
包含曲目、片段、声学特征、情绪评分、场景画像和推荐日志六大模型。
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# ────────────────────────────────
# 1. Track（曲目）模型
# ────────────────────────────────

class Track(models.Model):
    """
    曲目（Track）是系统中管理的一首完整音乐作品。

    包含基础元数据（标题、艺术家、版权状态、时长等）、
    播放相关配置（循环适配性、音频文件URL、封面图）以及时间戳。
    """

    # 版权状态枚举
    RIGHTS_STATUS_CHOICES = [
        ("authorized", "已授权"),
        ("restricted", "受限"),
        ("unknown", "不明"),
        ("disabled", "禁用"),
    ]

    # 复核状态枚举
    REVIEW_STATUS_CHOICES = [
        ("unreviewed", "未复核"),
        ("reviewed", "已复核"),
        ("needs_review", "需复核"),
    ]

    # 循环适配性枚举
    LOOPABILITY_CHOICES = [
        ("suitable", "适合"),
        ("fade_required", "需淡入淡出"),
        ("not_recommended", "不建议"),
    ]

    # ── 基础元数据 ──
    track_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="业务侧唯一曲目标识（如 MUS-2024-001）",
    )
    title = models.CharField(
        max_length=200,
        help_text="曲目标题",
    )
    artist = models.CharField(
        max_length=200,
        help_text="艺术家/作曲者名称",
    )
    rights_status = models.CharField(
        max_length=20,
        choices=RIGHTS_STATUS_CHOICES,
        default="unknown",
        help_text="版权状态：已授权、受限、不明、禁用",
    )
    duration_sec = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="曲目时长（秒），必须大于 0",
    )
    vocal_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="含人声概率，0=纯器乐，1=确定有人声",
    )
    lyrics_language = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="歌词语言（如 zh、en、ja），无人声可留空",
    )
    commercial_allowed = models.BooleanField(
        default=False,
        help_text="是否允许商用播放",
    )
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default="unreviewed",
        help_text="人工复核状态",
    )

    # ── 播放相关 ──
    loopability = models.CharField(
        max_length=20,
        choices=LOOPABILITY_CHOICES,
        default="suitable",
        help_text="循环播放适配性评估",
    )
    audio_file_url = models.URLField(
        blank=True,
        default="",
        help_text="音频文件存储 URL（对象存储或 CDN 地址）",
    )
    cover_image = models.URLField(
        blank=True,
        default="",
        help_text="封面图 URL",
    )

    # ── 时间戳 ──
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="最后更新时间",
    )

    class Meta:
        db_table = "core_track"
        verbose_name = "曲目"
        verbose_name_plural = "曲目"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["track_id"]),
            models.Index(fields=["rights_status", "review_status"]),
            models.Index(fields=["vocal_probability"]),
        ]

    def __str__(self) -> str:
        return f"{self.track_id} - {self.title} ({self.artist})"

    def clean(self) -> None:
        """模型级校验：含人声概率必须在 0-1 之间。"""
        if not (0.0 <= self.vocal_probability <= 1.0):
            raise ValidationError(
                {"vocal_probability": "vocal_probability 必须在 0.0 到 1.0 之间。"}
            )


# ────────────────────────────────
# 2. Segment（片段）模型
# ────────────────────────────────

class Segment(models.Model):
    """
    片段（Segment）是从完整 Track 中截取的可用于场景匹配的子区间。

    支持对同一段落生成多个版本（如不同淡入淡出处理），
    通过 segment_version 区分。
    """

    LOOPABILITY_CHOICES = [
        ("suitable", "适合"),
        ("fade_required", "需淡入淡出"),
        ("not_recommended", "不建议"),
    ]

    segment_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="片段唯一标识（如 SEG-2024-001-A）",
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name="segments",
        help_text="所属曲目",
    )
    start_sec = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="片段起始时间（秒），相对于曲目开头",
    )
    end_sec = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="片段结束时间（秒）",
    )
    loopability = models.CharField(
        max_length=20,
        choices=LOOPABILITY_CHOICES,
        default="suitable",
        help_text="该片段的循环播放适配性",
    )
    fade_in_out = models.BooleanField(
        default=False,
        help_text="是否已做淡入淡出处理",
    )
    segment_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="片段版本号，用于区分同一区间的不同处理版本",
    )

    class Meta:
        db_table = "core_segment"
        verbose_name = "片段"
        verbose_name_plural = "片段"
        ordering = ["track", "start_sec"]
        indexes = [
            models.Index(fields=["segment_id"]),
            models.Index(fields=["track", "start_sec", "end_sec"]),
        ]

    def __str__(self) -> str:
        return f"{self.segment_id} ({self.start_sec}s-{self.end_sec}s)"

    def clean(self) -> None:
        """模型级校验：结束时间必须晚于起始时间。"""
        if self.end_sec <= self.start_sec:
            raise ValidationError(
                {"end_sec": "结束时间必须晚于起始时间。"}
            )
        if self.start_sec < 0:
            raise ValidationError(
                {"start_sec": "起始时间不能为负数。"}
            )


# ────────────────────────────────
# 3. AudioFeature（声学特征）模型
# ────────────────────────────────

class AudioFeature(models.Model):
    """
    声学特征（AudioFeature）存储从音频信号中提取的可测量属性。

    关联到 Track（完整曲目）或 Segment（片段）。
    当 segment 为 None 时，表示这是整曲特征；否则为片段级特征。

    字段按技术报告分组：节奏与速度、调性与和声、能量响度动态、
    音色配器、歌词语义。
    """

    # ── 关联 ──
    track = models.OneToOneField(
        Track,
        on_delete=models.CASCADE,
        related_name="audio_features",
        help_text="关联曲目（整曲级特征）",
    )
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE,
        related_name="audio_features",
        null=True,
        blank=True,
        help_text="关联片段（片段级特征）；为空表示整曲特征",
    )

    # ═══════════════════════════════════════
    # 3.1 节奏与速度
    # ═══════════════════════════════════════
    bpm = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="每分钟节拍数（Beats Per Minute）",
    )
    beat_cv = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="节拍间隔变异系数（Coefficient of Variation），值越小越稳定",
    )
    onset_rate = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="起音密度，单位：onset/秒",
    )
    percussive_ratio = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="打击乐能量占总能量比例，0-1",
    )
    beat_clarity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="节拍清晰度，1 表示非常清晰的节拍",
    )

    # ═══════════════════════════════════════
    # 3.2 调性与和声
    # ═══════════════════════════════════════
    major_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="大调概率，0-1；与 minor_probability 互补",
    )
    minor_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="小调概率，0-1；与 major_probability 互补",
    )
    key_clarity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="调性清晰度，1 表示调性非常明确",
    )
    dissonance = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="不协和度/粗糙度（Dissonance/Roughness），0-1",
    )
    melody_rise = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="旋律上行比例，统计旋律线中上行片段的占比",
    )

    # ═══════════════════════════════════════
    # 3.3 能量响度动态
    # ═══════════════════════════════════════
    lufs = models.FloatField(
        help_text="综合响度（LUFS），国际标准响度单位",
    )
    lra = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="响度范围（Loudness Range，LU），反映动态变化幅度",
    )
    spike_count = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="突发强音密度，单位：次/分钟",
    )
    energy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="能量值，0-1，综合反映曲目整体强度",
    )
    dynamic_flux = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="动态波动度，0-1，值越大起伏越明显",
    )

    # ═══════════════════════════════════════
    # 3.4 音色配器
    # ═══════════════════════════════════════
    centroid = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="频谱质心（Spectral Centroid，Hz），反映音色明亮度",
    )
    flux = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="频谱通量（Spectral Flux），0-1，反映频谱变化率",
    )
    harmonic_ratio = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="和声能量占总能量的比例，0-1",
    )
    acoustic_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="原声乐器概率，0-1",
    )
    electronic_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="电子音色概率，0-1；与 acoustic_probability 互补",
    )
    vocal_clarity = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(7.0)],
        help_text="人声清晰度/阅读干扰度，1-7 级，1=完全不妨碍阅读，7=严重干扰",
    )

    # ═══════════════════════════════════════
    # 3.5 歌词语义
    # ═══════════════════════════════════════
    lyrics_valence = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="歌词情绪效价（Lyrics Valence），-1=负面，+1=正面",
    )
    theme_similarity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="歌词主题与场景主题的语义相似度，0-100",
    )

    # ── 元信息 ──
    extractor_version = models.CharField(
        max_length=50,
        default="librosa_0.10",
        help_text="特征提取器版本号",
    )
    analyzed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="特征分析完成时间",
    )

    class Meta:
        db_table = "core_audio_feature"
        verbose_name = "声学特征"
        verbose_name_plural = "声学特征"
        # 确保同一 Track 下只能有一条整曲特征（segment IS NULL）
        constraints = [
            models.UniqueConstraint(
                fields=["track"],
                condition=models.Q(segment__isnull=True),
                name="unique_track_level_features",
            )
        ]
        indexes = [
            models.Index(fields=["bpm"]),
            models.Index(fields=["energy"]),
            models.Index(fields=["centroid"]),
        ]

    def __str__(self) -> str:
        scope = f"Segment:{self.segment.segment_id}" if self.segment else "Full Track"
        return f"AudioFeature({self.track.track_id}, {scope})"

    def clean(self) -> None:
        """校验概率类字段之和是否合理。"""
        # major + minor 概率应接近 1
        prob_sum = self.major_probability + self.minor_probability
        if not (0.8 <= prob_sum <= 1.2):
            raise ValidationError(
                {
                    "major_probability": "major_probability + minor_probability 应在 0.8-1.2 范围内。"
                }
            )


# ────────────────────────────────
# 4. EmotionScore（情绪评分）模型
# ────────────────────────────────

class EmotionScore(models.Model):
    """
    情绪评分（EmotionScore）存储音乐在七维情绪空间中的量化得分。

    每维度包含三个值：
    - _ai:     AI 模型初判结果
    - _human:  人工标注员均分（可为空，表示尚未人工标注）
    - _final:  AI 与人工融合后的最终得分

    七维情绪：valence（效价）、arousal（唤醒度）、warmth（温暖度）、
    tension（紧张度）、hope（希望感）、motivation（动力感）、intrusion（侵入感）。
    """

    # ── 关联 ──
    track = models.OneToOneField(
        Track,
        on_delete=models.CASCADE,
        related_name="emotion_score",
        help_text="关联曲目（整曲级情绪评分）",
    )
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE,
        related_name="emotion_scores",
        null=True,
        blank=True,
        help_text="关联片段（片段级情绪评分）；为空表示整曲评分",
    )

    # ═══════════════════════════════════════
    # 4.1 七维情绪评分
    # ═══════════════════════════════════════

    # --- Valence（效价）---
    valence_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="效价 AI 初判：0=非常负面，7=非常正面",
    )
    valence_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="效价人工均分（可为空）",
    )
    valence_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="效价最终融合分",
    )

    # --- Arousal（唤醒度）---
    arousal_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="唤醒度 AI 初判：0=非常平静，7=非常激动",
    )
    arousal_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="唤醒度人工均分（可为空）",
    )
    arousal_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="唤醒度最终融合分",
    )

    # --- Warmth（温暖度）---
    warmth_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="温暖度 AI 初判：0=冷漠，7=非常温暖",
    )
    warmth_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="温暖度人工均分（可为空）",
    )
    warmth_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="温暖度最终融合分",
    )

    # --- Tension（紧张度）---
    tension_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="紧张度 AI 初判：0=放松，7=非常紧张",
    )
    tension_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="紧张度人工均分（可为空）",
    )
    tension_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="紧张度最终融合分",
    )

    # --- Hope（希望感）---
    hope_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="希望感 AI 初判：0=绝望，7=充满希望",
    )
    hope_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="希望感人工均分（可为空）",
    )
    hope_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="希望感最终融合分",
    )

    # --- Motivation（动力感）---
    motivation_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="动力感 AI 初判：0=消沉，7=非常积极",
    )
    motivation_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="动力感人工均分（可为空）",
    )
    motivation_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="动力感最终融合分",
    )

    # --- Intrusion（侵入感）---
    intrusion_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="侵入感 AI 初判：0=完全不干扰，7=严重干扰",
    )
    intrusion_human = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="侵入感人工均分（可为空）",
    )
    intrusion_final = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="侵入感最终融合分",
    )

    # ═══════════════════════════════════════
    # 4.2 置信度与融合参数
    # ═══════════════════════════════════════
    sample_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="人工标注样本数，0 表示尚未人工标注",
    )
    agreement_rate = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="标注员间一致性（如 Krippendorff's Alpha），0-1",
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="综合置信度，0-1，考虑 AI 确定性与人工一致性",
    )
    fusion_lambda = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="融合时 AI 权重 λ，默认 0.7；人工权重为 1-λ",
    )
    model_version = models.CharField(
        max_length=20,
        default="v1.0",
        help_text="情绪预测模型版本号",
    )

    # ── 计算时间戳 ──
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="情绪评分计算时间",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="最后更新时间",
    )

    class Meta:
        db_table = "core_emotion_score"
        verbose_name = "情绪评分"
        verbose_name_plural = "情绪评分"
        constraints = [
            models.UniqueConstraint(
                fields=["track"],
                condition=models.Q(segment__isnull=True),
                name="unique_track_level_emotion",
            )
        ]
        indexes = [
            models.Index(fields=["confidence"]),
            models.Index(fields=["model_version"]),
        ]

    def __str__(self) -> str:
        scope = f"Segment:{self.segment.segment_id}" if self.segment else "Full Track"
        return f"EmotionScore({self.track.track_id}, {scope})"

    def compute_final_scores(self) -> None:
        """
        根据 AI 分数、人工分数和融合权重 λ 计算最终融合分。

        公式：final = λ * ai + (1-λ) * human
        若人工分数为空，则 final = ai。
        """
        dimensions = [
            "valence", "arousal", "warmth", "tension",
            "hope", "motivation", "intrusion",
        ]
        for dim in dimensions:
            ai_val = getattr(self, f"{dim}_ai")
            human_val = getattr(self, f"{dim}_human")
            if human_val is not None:
                final_val = self.fusion_lambda * ai_val + (1 - self.fusion_lambda) * human_val
            else:
                final_val = ai_val
            setattr(self, f"{dim}_final", round(final_val, 4))

    def save(self, *args, **kwargs) -> None:
        """保存前自动计算最终融合分。"""
        self.compute_final_scores()
        super().save(*args, **kwargs)


# ────────────────────────────────
# 5. SceneProfile（场景画像）模型
# ────────────────────────────────

class SceneProfile(models.Model):
    """
    场景画像（SceneProfile）描述客户使用场景的目标情绪与约束条件。

    核心字段 target_emotion 以 JSON 格式定义七维情绪的目标区间与权重，
    是匹配算法的输入参数。
    """

    TASK_CHOICES = [
        ("browse", "浏览体验"),
        ("read", "阅读详情"),
        ("add_cart", "加入购物车"),
        ("purchase", "购买决策"),
        ("donate", "捐赠决策"),
    ]

    # ── 基础信息 ──
    profile_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="场景画像唯一标识（如 SCENE-2024-001）",
    )
    scene_name = models.CharField(
        max_length=200,
        help_text="场景名称（如'品牌官网-产品页'）",
    )
    industry = models.CharField(
        max_length=100,
        help_text="行业分类（如电商、教育、公益）",
    )
    topic_keywords = models.JSONField(
        default=list,
        help_text="主题关键词列表，用于语义匹配（如 ['科技', '创新', '未来']）",
    )

    # ── 目标用户 ──
    target_user_age = models.CharField(
        max_length=50,
        help_text="目标用户年龄段（如 '18-25'、'全年龄'）",
    )
    target_user_language = models.CharField(
        max_length=50,
        help_text="目标用户语言（如 zh、en、multilingual）",
    )
    target_user_device = models.CharField(
        max_length=50,
        help_text="主要使用设备（如 desktop、mobile、tablet）",
    )

    # ── 当前任务 ──
    current_task = models.CharField(
        max_length=50,
        choices=TASK_CHOICES,
        default="browse",
        help_text="用户在场景中的主要任务",
    )

    # ── 品牌感受 ──
    brand_keywords = models.JSONField(
        default=list,
        help_text="品牌感受关键词（如 ['高端', '可信赖', '温暖']）",
    )

    # ── 目标情绪区间（核心匹配参数）──
    # JSON 格式示例：
    # {
    #   "valence":   {"min": 5.5, "max": 6.5, "weight": 0.25},
    #   "arousal":   {"min": 3.0, "max": 4.5, "weight": 0.15},
    #   "warmth":    {"min": 4.0, "max": 5.5, "weight": 0.15},
    #   "tension":   {"min": 1.5, "max": 3.0, "weight": 0.10},
    #   "hope":      {"min": 5.0, "max": 6.0, "weight": 0.15},
    #   "motivation":{"min": 4.0, "max": 5.5, "weight": 0.10},
    #   "intrusion": {"min": 0.0, "max": 2.5, "weight": 0.10}
    # }
    target_emotion = models.JSONField(
        help_text="目标情绪区间与权重（JSON 格式，每维度含 min/max/weight）",
    )

    # ── 视觉风格 ──
    visual_style = models.JSONField(
        default=dict,
        help_text="视觉风格描述（JSON，如 {'color_temperature': 'warm', 'complexity': 'minimal'}）",
    )

    # ── 播放策略 ──
    playback_position = models.CharField(
        max_length=50,
        help_text="音乐播放位置（如 'background', 'hero_section', 'checkout'）",
    )
    autoplay = models.BooleanField(
        default=False,
        help_text="是否自动播放",
    )
    loop = models.BooleanField(
        default=True,
        help_text="是否循环播放",
    )

    # ── 约束条件 ──
    lyrics_allowed = models.BooleanField(
        default=True,
        help_text="是否允许带歌词的曲目",
    )
    vocal_allowed = models.BooleanField(
        default=True,
        help_text="是否允许含人声的曲目",
    )
    preferred_bpm_range = models.JSONField(
        default=dict,
        help_text="首选 BPM 范围（JSON：{'min': 85, 'max': 120}）",
    )
    max_intrusion_risk = models.FloatField(
        default=3.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)],
        help_text="最大允许侵入感评分，0-7",
    )
    environment = models.CharField(
        max_length=50,
        help_text="使用环境（如 'office', 'public_space', 'home'）",
    )

    # ── 状态 ──
    confirmed = models.BooleanField(
        default=False,
        help_text="场景画像是否已确认生效",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间",
    )

    class Meta:
        db_table = "core_scene_profile"
        verbose_name = "场景画像"
        verbose_name_plural = "场景画像"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["profile_id"]),
            models.Index(fields=["industry", "current_task"]),
            models.Index(fields=["confirmed"]),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id} - {self.scene_name}"

    def clean(self) -> None:
        """校验 target_emotion JSON 结构。"""
        required_dims = [
            "valence", "arousal", "warmth", "tension",
            "hope", "motivation", "intrusion",
        ]
        if not isinstance(self.target_emotion, dict):
            raise ValidationError(
                {"target_emotion": "target_emotion 必须是 JSON 对象。"}
            )
        for dim in required_dims:
            if dim not in self.target_emotion:
                raise ValidationError(
                    {"target_emotion": f"target_emotion 缺少必需维度 '{dim}'。"}
                )
            cfg = self.target_emotion[dim]
            for key in ("min", "max", "weight"):
                if key not in cfg:
                    raise ValidationError(
                        {"target_emotion": f"target_emotion.{dim} 缺少 '{key}' 字段。"}
                    )
            if not (0.0 <= cfg["min"] <= 7.0 and 0.0 <= cfg["max"] <= 7.0):
                raise ValidationError(
                    {"target_emotion": f"target_emotion.{dim} 的 min/max 必须在 0-7 范围内。"}
                )
            if cfg["min"] > cfg["max"]:
                raise ValidationError(
                    {"target_emotion": f"target_emotion.{dim} 的 min 不能大于 max。"}
                )
            if not (0.0 <= cfg["weight"] <= 1.0):
                raise ValidationError(
                    {"target_emotion": f"target_emotion.{dim} 的 weight 必须在 0-1 范围内。"}
                )


# ────────────────────────────────
# 6. RecommendationLog（推荐日志）模型
# ────────────────────────────────

class RecommendationLog(models.Model):
    """
    推荐日志（RecommendationLog）记录每次场景匹配的结果。

    包含各维度匹配分数、过滤原因、最终是否被选中及是否已播放。
    支持事后分析与 A/B 测试效果评估。
    """

    profile = models.ForeignKey(
        SceneProfile,
        on_delete=models.CASCADE,
        related_name="recommendations",
        help_text="对应的场景画像",
    )
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE,
        help_text="推荐的片段",
    )

    # ── 匹配分数 ──
    emotion_match = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="情绪匹配度，0-1",
    )
    semantic_match = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="语义匹配度（主题关键词相似度），0-1",
    )
    environment_fit = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="环境适配度（BPM、侵入感等约束满足度），0-1",
    )
    risk_penalty = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="风险惩罚项，值越大表示风险越高",
    )
    total_score = models.FloatField(
        help_text="综合总分 = emotion_match * w1 + semantic_match * w2 + environment_fit * w3 - risk_penalty",
    )

    # ── 过滤与状态 ──
    filter_reason = models.TextField(
        blank=True,
        default="",
        help_text="若被过滤，记录过滤原因；否则为空",
    )
    selected = models.BooleanField(
        default=False,
        help_text="是否被选中进入最终播放列表",
    )
    played = models.BooleanField(
        default=False,
        help_text="是否已被实际播放",
    )

    # ── 时间戳 ──
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="推荐生成时间",
    )

    class Meta:
        db_table = "core_recommendation_log"
        verbose_name = "推荐日志"
        verbose_name_plural = "推荐日志"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["profile", "total_score"]),
            models.Index(fields=["segment"]),
            models.Index(fields=["selected", "played"]),
        ]

    def __str__(self) -> str:
        return (
            f"Recommendation({self.profile.profile_id} -> "
            f"{self.segment.segment_id}, score={self.total_score:.3f})"
        )

/* ------------------------------------------------------------------ */
/*  Music Library Data Layer — MZSS v1.0                               */
/*  Supports API-driven data fetching with local fallback              */
/* ------------------------------------------------------------------ */

const BASE_AUDIO_URL =
  "https://raw.githubusercontent.com/ajaxs-cyber/my-music-storage/main/音乐存储/";

/* ========================== Interfaces ========================== */

export interface Track {
  id: string;
  title: string;
  artist: string;
  genre: string;
  bpm: number;
  key: string;
  duration: string;
  durationSec: number;
  valence: number;
  arousal: number;
  warmth: number;
  tension: number;
  hope: number;
  motivation: number;
  intrusion: number;
  tags: string[];
  cover: string;
  sceneType: string;
  lufs: string;
  lufsValue: number;
  /* 版权与状态 */
  rightsStatus: "authorized" | "restricted" | "unknown" | "disabled";
  reviewStatus: "unreviewed" | "reviewed" | "needs_review";
  commercialAllowed: boolean;
  vocalProbability: number;
  /* 音频文件URL */
  audioUrl?: string;
  /* 完整声学特征 */
  audioFeatures: {
    beatCv: number;
    onsetRate: number;
    percussiveRatio: number;
    beatClarity: number;
    majorProbability: number;
    minorProbability: number;
    keyClarity: number;
    dissonance: number;
    melodyRise: number;
    lra: number;
    spikeCount: number;
    energy: number;
    dynamicFlux: number;
    centroid: number;
    flux: number;
    harmonicRatio: number;
    acousticProbability: number;
    electronicProbability: number;
    vocalClarity: number;
    lyricsValence: number;
    themeSimilarity: number;
  };
  /* 置信度 */
  confidence: number;
  sampleCount: number;
  fusionLambda: number;
  /* 可解释说明 */
  explanation: string[];
}

export interface EmotionDimension {
  key: string;
  label: string;
  labelEn: string;
  range: string;
  desc: string;
}

export interface SceneTemplate {
  type: string;
  valence: string;
  arousal: string;
  warmth: string;
  tension: string;
  hope: string;
  motivation: string;
  constraint: string;
}

/* ========================== Static Data ========================== */

export const emotionDimensions: EmotionDimension[] = [
  {
    key: "valence",
    label: "效价",
    labelEn: "Valence",
    range: "0.00 ~ 1.00",
    desc: "情绪积极程度。高值表示愉快、积极；低值表示悲伤、消极。基于大调概率、旋律上行比例、和声占比和调性清晰度综合计算。",
  },
  {
    key: "arousal",
    label: "唤醒",
    labelEn: "Arousal",
    range: "0.00 ~ 1.00",
    desc: "生理激活水平。高值表示兴奋、紧张；低值表示平静、放松。基于能量值、起音密度和节拍清晰度综合计算。",
  },
  {
    key: "warmth",
    label: "温暖",
    labelEn: "Warmth",
    range: "0.00 ~ 1.00",
    desc: "听觉温暖感。与原声乐器占比、效价和适度唤醒度正相关。低值偏冷峻、机械；高值偏温暖、亲切。",
  },
  {
    key: "tension",
    label: "紧张",
    labelEn: "Tension",
    range: "0.00 ~ 1.00",
    desc: "紧张与悬疑感。与不协和度、频谱通量、响度范围和突发强音正相关。高值适合悬念场景，低值适合舒适场景。",
  },
  {
    key: "hope",
    label: "希望",
    labelEn: "Hope",
    range: "0.00 ~ 1.00",
    desc: "希望与光明感。高值表现为积极效价配合小调转大调、旋律上行；低值偏绝望、压抑。",
  },
  {
    key: "motivation",
    label: "行动",
    labelEn: "Motivation",
    range: "0.00 ~ 1.00",
    desc: "行动驱动力。与唤醒度、效价和打击乐占比正相关。高值适合运动、决策场景；低值适合静态冥想。",
  },
  {
    key: "intrusion",
    label: "干扰",
    labelEn: "Intrusion",
    range: "0.00 ~ 1.00",
    desc: "对人任务的干扰风险。与人声清晰度、人声概率、唤醒度和歌词效价正相关。高值不适合专注场景。",
  },
];

export const sceneTemplates: SceneTemplate[] = [
  {
    type: "高端美妆旗舰店",
    valence: "0.55 ~ 0.75",
    arousal: "0.30 ~ 0.55",
    warmth: "0.50 ~ 0.70",
    tension: "0.10 ~ 0.30",
    hope: "0.45 ~ 0.65",
    motivation: "0.30 ~ 0.50",
    constraint: "禁止歌词，偏电子氛围，允许低频脉冲",
  },
  {
    type: "公益捐赠页面",
    valence: "0.40 ~ 0.65",
    arousal: "0.25 ~ 0.50",
    warmth: "0.60 ~ 0.85",
    tension: "0.15 ~ 0.35",
    hope: "0.55 ~ 0.80",
    motivation: "0.50 ~ 0.75",
    constraint: "偏原声乐器，允许人声但需舒缓，强调希望感",
  },
  {
    type: "运动健身空间",
    valence: "0.50 ~ 0.80",
    arousal: "0.70 ~ 0.95",
    warmth: "0.30 ~ 0.55",
    tension: "0.20 ~ 0.45",
    hope: "0.40 ~ 0.65",
    motivation: "0.75 ~ 1.00",
    constraint: "高BPM 120+，强节拍，允许电子和打击乐",
  },
  {
    type: "沉浸式文创展览",
    valence: "0.45 ~ 0.70",
    arousal: "0.20 ~ 0.45",
    warmth: "0.55 ~ 0.80",
    tension: "0.10 ~ 0.30",
    hope: "0.50 ~ 0.75",
    motivation: "0.15 ~ 0.35",
    constraint: "无歌词优先，偏氛围音乐/轻音乐，低干扰",
  },
];

/* ========================== Track Data (8 tracks) ========================== */

export const tracks: Track[] = [
  /* ── Track 1: 爵士 ── */
  {
    id: "track-001",
    title: "Midnight Jazz Lounge",
    artist: "The Smooth Quartet",
    genre: "爵士",
    bpm: 88,
    key: "Bb major",
    duration: "4:32",
    durationSec: 272,
    valence: 0.72,
    arousal: 0.35,
    warmth: 0.78,
    tension: 0.18,
    hope: 0.62,
    motivation: 0.28,
    intrusion: 0.22,
    tags: ["萨克斯", "钢琴", "放松", "酒吧", "夜晚"],
    cover: "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=400&h=400&fit=crop",
    sceneType: "高端美妆旗舰店",
    lufs: "-16.2 LUFS",
    lufsValue: -16.2,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.0,
    audioUrl: `${BASE_AUDIO_URL}midnight_jazz_lounge.mp3`,
    audioFeatures: {
      beatCv: 0.08,
      onsetRate: 3.2,
      percussiveRatio: 0.25,
      beatClarity: 0.65,
      majorProbability: 0.82,
      minorProbability: 0.18,
      keyClarity: 0.88,
      dissonance: 0.12,
      melodyRise: 0.58,
      lra: 8.5,
      spikeCount: 6,
      energy: 0.22,
      dynamicFlux: 0.15,
      centroid: 2100,
      flux: 0.18,
      harmonicRatio: 0.82,
      acousticProbability: 0.92,
      electronicProbability: 0.08,
      vocalClarity: 0.0,
      lyricsValence: 0.0,
      themeSimilarity: 0.75,
    },
    confidence: 0.91,
    sampleCount: 245,
    fusionLambda: 0.65,
    explanation: [
      "高和声占比(0.82)与大调概率(0.82)共同推高效价至0.72",
      "低能量值(0.22)与低起音密度(3.2)使唤醒度保持在0.35的放松区间",
      "原声乐器占比0.92带来0.78的高温暖感",
      "无歌词、低唤醒使干扰风险仅0.22，适合专注场景",
    ],
  },

  /* ── Track 2: KPOP ── */
  {
    id: "track-002",
    title: "Neon Pulse",
    artist: "STARLIGHT",
    genre: "KPOP",
    bpm: 128,
    key: "F# minor",
    duration: "3:18",
    durationSec: 198,
    valence: 0.68,
    arousal: 0.92,
    warmth: 0.32,
    tension: 0.55,
    hope: 0.58,
    motivation: 0.88,
    intrusion: 0.72,
    tags: ["合成器", "舞曲", "活力", "派对", "电子"],
    cover: "https://images.unsplash.com/photo-1493225255756-d9584f8606e9?w=400&h=400&fit=crop",
    sceneType: "运动健身空间",
    lufs: "-8.5 LUFS",
    lufsValue: -8.5,
    rightsStatus: "restricted",
    reviewStatus: "needs_review",
    commercialAllowed: false,
    vocalProbability: 0.85,
    audioUrl: `${BASE_AUDIO_URL}neon_pulse.mp3`,
    audioFeatures: {
      beatCv: 0.03,
      onsetRate: 8.8,
      percussiveRatio: 0.72,
      beatClarity: 0.95,
      majorProbability: 0.35,
      minorProbability: 0.65,
      keyClarity: 0.78,
      dissonance: 0.38,
      melodyRise: 0.62,
      lra: 5.2,
      spikeCount: 28,
      energy: 0.88,
      dynamicFlux: 0.72,
      centroid: 6200,
      flux: 0.68,
      harmonicRatio: 0.35,
      acousticProbability: 0.08,
      electronicProbability: 0.92,
      vocalClarity: 0.82,
      lyricsValence: 0.65,
      themeSimilarity: 0.55,
    },
    confidence: 0.88,
    sampleCount: 512,
    fusionLambda: 0.78,
    explanation: [
      "小调(0.65)但高旋律上行(0.62)使效价维持在0.68的积极水平",
      "极高能量值(0.88)与高频谱质心(6200Hz)产生0.92的高唤醒度",
      "电子合成器主导(electronic 0.92)降低温暖感至0.32",
      "高人声清晰度(0.82)与歌词效价(0.65)使干扰风险达0.72",
    ],
  },

  /* ── Track 3: 轻音乐 ── */
  {
    id: "track-003",
    title: "Morning Dew",
    artist: "Yuki Tanaka",
    genre: "轻音乐",
    bpm: 72,
    key: "C major",
    duration: "5:05",
    durationSec: 305,
    valence: 0.78,
    arousal: 0.18,
    warmth: 0.85,
    tension: 0.05,
    hope: 0.72,
    motivation: 0.15,
    intrusion: 0.08,
    tags: ["钢琴", "自然", "治愈", "清晨", "冥想"],
    cover: "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=400&h=400&fit=crop",
    sceneType: "沉浸式文创展览",
    lufs: "-20.1 LUFS",
    lufsValue: -20.1,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.0,
    audioUrl: `${BASE_AUDIO_URL}morning_dew.mp3`,
    audioFeatures: {
      beatCv: 0.15,
      onsetRate: 1.8,
      percussiveRatio: 0.08,
      beatClarity: 0.42,
      majorProbability: 0.95,
      minorProbability: 0.05,
      keyClarity: 0.92,
      dissonance: 0.02,
      melodyRise: 0.65,
      lra: 12.8,
      spikeCount: 1,
      energy: 0.08,
      dynamicFlux: 0.05,
      centroid: 850,
      flux: 0.04,
      harmonicRatio: 0.95,
      acousticProbability: 0.98,
      electronicProbability: 0.02,
      vocalClarity: 0.0,
      lyricsValence: 0.0,
      themeSimilarity: 0.88,
    },
    confidence: 0.95,
    sampleCount: 189,
    fusionLambda: 0.45,
    explanation: [
      "纯钢琴大调(0.95)配高和声占比(0.95)产生0.78的高效价",
      "极低能量(0.08)与低起音密度(1.8)使唤醒度仅0.18",
      "98%原声乐器带来0.85的高温暖感",
      "无歌词、极低动态波动使干扰风险仅0.08，适合冥想与展览",
    ],
  },

  /* ── Track 4: 氛围音乐 ── */
  {
    id: "track-004",
    title: "Deep Space Ambient",
    artist: "Echo Drift",
    genre: "氛围音乐",
    bpm: 60,
    key: "D minor",
    duration: "8:42",
    durationSec: 522,
    valence: 0.25,
    arousal: 0.42,
    warmth: 0.22,
    tension: 0.68,
    hope: 0.18,
    motivation: 0.22,
    intrusion: 0.35,
    tags: ["环境", "实验", "太空", "深邃", "沉浸"],
    cover: "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=400&h=400&fit=crop",
    sceneType: "沉浸式文创展览",
    lufs: "-22.5 LUFS",
    lufsValue: -22.5,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.0,
    audioUrl: `${BASE_AUDIO_URL}deep_space_ambient.mp3`,
    audioFeatures: {
      beatCv: 0.35,
      onsetRate: 0.5,
      percussiveRatio: 0.05,
      beatClarity: 0.15,
      majorProbability: 0.12,
      minorProbability: 0.88,
      keyClarity: 0.45,
      dissonance: 0.72,
      melodyRise: 0.22,
      lra: 18.5,
      spikeCount: 3,
      energy: 0.15,
      dynamicFlux: 0.42,
      centroid: 4200,
      flux: 0.55,
      harmonicRatio: 0.18,
      acousticProbability: 0.15,
      electronicProbability: 0.85,
      vocalClarity: 0.0,
      lyricsValence: 0.0,
      themeSimilarity: 0.42,
    },
    confidence: 0.82,
    sampleCount: 156,
    fusionLambda: 0.55,
    explanation: [
      "小调主导(0.88)配低旋律上行(0.22)使效价仅0.25",
      "高频谱通量(0.55)与高LRA(18.5)在低频下产生0.42的唤醒度",
      "电子音色主导(0.85)与原声占比低(0.15)使温暖感仅0.22",
      "高不协和度(0.72)与频谱通量(0.55)产生0.68的高紧张感",
    ],
  },

  /* ── Track 5: R&B ── */
  {
    id: "track-005",
    title: "Velvet Touch",
    artist: "Aaliyah Moore",
    genre: "R&B",
    bpm: 95,
    key: "Eb minor",
    duration: "3:55",
    durationSec: 235,
    valence: 0.55,
    arousal: 0.48,
    warmth: 0.72,
    tension: 0.32,
    hope: 0.45,
    motivation: 0.42,
    intrusion: 0.58,
    tags: ["灵魂乐", "人声", "情感", "夜晚", "浪漫"],
    cover: "https://images.unsplash.com/photo-1496293455970-f8581aae0e3b?w=400&h=400&fit=crop",
    sceneType: "高端美妆旗舰店",
    lufs: "-12.8 LUFS",
    lufsValue: -12.8,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.78,
    audioUrl: `${BASE_AUDIO_URL}velvet_touch.mp3`,
    audioFeatures: {
      beatCv: 0.06,
      onsetRate: 4.5,
      percussiveRatio: 0.38,
      beatClarity: 0.78,
      majorProbability: 0.28,
      minorProbability: 0.72,
      keyClarity: 0.82,
      dissonance: 0.22,
      melodyRise: 0.48,
      lra: 9.2,
      spikeCount: 12,
      energy: 0.42,
      dynamicFlux: 0.35,
      centroid: 2800,
      flux: 0.32,
      harmonicRatio: 0.68,
      acousticProbability: 0.45,
      electronicProbability: 0.55,
      vocalClarity: 0.75,
      lyricsValence: 0.52,
      themeSimilarity: 0.68,
    },
    confidence: 0.89,
    sampleCount: 334,
    fusionLambda: 0.72,
    explanation: [
      "小调(0.72)但歌词效价(0.52)平衡效价至0.55",
      "中等能量(0.42)与清晰节拍(0.78)产生0.48的适中唤醒度",
      "混合原声与电子(0.45/0.55)配合人声产生0.72的温暖感",
      "人声清晰度(0.75)使干扰风险达0.58，适合非专注场景",
    ],
  },

  /* ── Track 6: 民谣 ── */
  {
    id: "track-006",
    title: "Autumn Path",
    artist: "陈墨",
    genre: "民谣",
    bpm: 68,
    key: "G major",
    duration: "4:48",
    durationSec: 288,
    valence: 0.65,
    arousal: 0.22,
    warmth: 0.88,
    tension: 0.12,
    hope: 0.68,
    motivation: 0.25,
    intrusion: 0.45,
    tags: ["吉他", "叙事", "治愈", "自然", "秋日"],
    cover: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    sceneType: "公益捐赠页面",
    lufs: "-18.5 LUFS",
    lufsValue: -18.5,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.92,
    audioUrl: `${BASE_AUDIO_URL}autumn_path.mp3`,
    audioFeatures: {
      beatCv: 0.18,
      onsetRate: 2.2,
      percussiveRatio: 0.12,
      beatClarity: 0.52,
      majorProbability: 0.88,
      minorProbability: 0.12,
      keyClarity: 0.85,
      dissonance: 0.05,
      melodyRise: 0.55,
      lra: 14.2,
      spikeCount: 2,
      energy: 0.12,
      dynamicFlux: 0.12,
      centroid: 1200,
      flux: 0.1,
      harmonicRatio: 0.88,
      acousticProbability: 0.95,
      electronicProbability: 0.05,
      vocalClarity: 0.88,
      lyricsValence: 0.72,
      themeSimilarity: 0.82,
    },
    confidence: 0.93,
    sampleCount: 278,
    fusionLambda: 0.52,
    explanation: [
      "大调(0.88)配合高歌词效价(0.72)使效价达0.65",
      "低能量(0.12)与原声吉他带来0.22的低唤醒度",
      "95%原声乐器与木吉他共鸣产生0.88的极高温暖感",
      "人声清晰(0.88)但低唤醒与温暖歌词使干扰仅0.45",
    ],
  },

  /* ── Track 7: 蓝调 ── */
  {
    id: "track-007",
    title: "Delta Soul",
    artist: "Marcus Johnson",
    genre: "蓝调",
    bpm: 76,
    key: "A minor",
    duration: "5:20",
    durationSec: 320,
    valence: 0.35,
    arousal: 0.38,
    warmth: 0.65,
    tension: 0.45,
    hope: 0.28,
    motivation: 0.32,
    intrusion: 0.38,
    tags: ["口琴", "吉他", "忧郁", "经典", "故事"],
    cover: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&h=400&fit=crop",
    sceneType: "公益捐赠页面",
    lufs: "-15.8 LUFS",
    lufsValue: -15.8,
    rightsStatus: "unknown",
    reviewStatus: "unreviewed",
    commercialAllowed: false,
    vocalProbability: 0.62,
    audioUrl: `${BASE_AUDIO_URL}delta_soul.mp3`,
    audioFeatures: {
      beatCv: 0.12,
      onsetRate: 3.0,
      percussiveRatio: 0.22,
      beatClarity: 0.58,
      majorProbability: 0.15,
      minorProbability: 0.85,
      keyClarity: 0.72,
      dissonance: 0.35,
      melodyRise: 0.32,
      lra: 11.5,
      spikeCount: 8,
      energy: 0.25,
      dynamicFlux: 0.28,
      centroid: 1850,
      flux: 0.22,
      harmonicRatio: 0.55,
      acousticProbability: 0.78,
      electronicProbability: 0.22,
      vocalClarity: 0.68,
      lyricsValence: 0.35,
      themeSimilarity: 0.62,
    },
    confidence: 0.85,
    sampleCount: 198,
    fusionLambda: 0.58,
    explanation: [
      "小调主导(0.85)配低歌词效价(0.35)使效价仅0.35",
      "中等偏低能量(0.25)与蓝调节奏产生0.38的唤醒度",
      "原声乐器占比(0.78)带来0.65的温暖感",
      "人声清晰度(0.68)适中，主题相似度(0.62)表现良好",
    ],
  },

  /* ── Track 8: 电子 ── */
  {
    id: "track-008",
    title: "Cyber Run",
    artist: "Neon Walker",
    genre: "电子",
    bpm: 140,
    key: "E minor",
    duration: "3:45",
    durationSec: 225,
    valence: 0.58,
    arousal: 0.96,
    warmth: 0.15,
    tension: 0.52,
    hope: 0.48,
    motivation: 0.95,
    intrusion: 0.48,
    tags: ["合成器", "跑步", "高能", "未来", "动力"],
    cover: "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=400&h=400&fit=crop",
    sceneType: "运动健身空间",
    lufs: "-7.2 LUFS",
    lufsValue: -7.2,
    rightsStatus: "authorized",
    reviewStatus: "reviewed",
    commercialAllowed: true,
    vocalProbability: 0.0,
    audioUrl: `${BASE_AUDIO_URL}cyber_run.mp3`,
    audioFeatures: {
      beatCv: 0.02,
      onsetRate: 9.5,
      percussiveRatio: 0.82,
      beatClarity: 0.98,
      majorProbability: 0.22,
      minorProbability: 0.78,
      keyClarity: 0.88,
      dissonance: 0.42,
      melodyRise: 0.72,
      lra: 4.8,
      spikeCount: 35,
      energy: 0.95,
      dynamicFlux: 0.82,
      centroid: 7800,
      flux: 0.78,
      harmonicRatio: 0.22,
      acousticProbability: 0.02,
      electronicProbability: 0.98,
      vocalClarity: 0.0,
      lyricsValence: 0.0,
      themeSimilarity: 0.65,
    },
    confidence: 0.94,
    sampleCount: 445,
    fusionLambda: 0.82,
    explanation: [
      "小调(0.78)但高旋律上行(0.72)与高能节拍使效价达0.58",
      "极高能量(0.95)与最高起音密度(9.5)产生0.96的唤醒度",
      "98%电子音色使温暖感仅0.15，冷峻未来感十足",
      "无人声但高动态波动(0.82)使干扰风险0.48，适合运动",
    ],
  },
];

/* ========================== API Functions ========================== */

/**
 * Simulate API: fetch all tracks.
 * Replace with real HTTP call when backend is ready.
 */
export async function fetchTracks(): Promise<Track[]> {
  // Simulated network delay
  await new Promise((resolve) => setTimeout(resolve, 300));
  return [...tracks];
}

/**
 * Simulate API: fetch a single track by ID.
 */
export async function fetchTrackById(id: string): Promise<Track | undefined> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return tracks.find((t) => t.id === id);
}

/**
 * Simulate API: fetch tracks filtered by genre.
 */
export async function fetchTracksByGenre(genre: string): Promise<Track[]> {
  await new Promise((resolve) => setTimeout(resolve, 250));
  return tracks.filter(
    (t) => t.genre.toLowerCase() === genre.toLowerCase()
  );
}

/**
 * Simulate API: fetch tracks filtered by scene type.
 */
export async function fetchTracksBySceneType(sceneType: string): Promise<Track[]> {
  await new Promise((resolve) => setTimeout(resolve, 250));
  return tracks.filter((t) => t.sceneType.includes(sceneType));
}

/**
 * Simulate API: fetch tracks within a BPM range.
 */
export async function fetchTracksByBpmRange(
  min: number,
  max: number
): Promise<Track[]> {
  await new Promise((resolve) => setTimeout(resolve, 250));
  return tracks.filter((t) => t.bpm >= min && t.bpm <= max);
}

/* ========================== Derived Stats ========================== */

export function getGenreDistribution(tracksList: Track[]) {
  const map: Record<string, number> = {};
  tracksList.forEach((t) => {
    map[t.genre] = (map[t.genre] || 0) + 1;
  });
  return map;
}

export function getSceneTypeDistribution(tracksList: Track[]) {
  const map: Record<string, number> = {};
  tracksList.forEach((t) => {
    map[t.sceneType] = (map[t.sceneType] || 0) + 1;
  });
  return map;
}

export function getBpmRange(tracksList: Track[]): [number, number] {
  if (tracksList.length === 0) return [0, 0];
  const bpms = tracksList.map((t) => t.bpm);
  return [Math.min(...bpms), Math.max(...bpms)];
}

export function getLufsRange(tracksList: Track[]): [number, number] {
  if (tracksList.length === 0) return [0, 0];
  const vals = tracksList.map((t) => t.lufsValue);
  return [Math.min(...vals), Math.max(...vals)];
}

export function getAverageEmotions(tracksList: Track[]) {
  if (tracksList.length === 0)
    return { valence: 0, arousal: 0, warmth: 0, tension: 0, hope: 0, motivation: 0, intrusion: 0 };
  const sums = tracksList.reduce(
    (acc, t) => {
      acc.valence += t.valence;
      acc.arousal += t.arousal;
      acc.warmth += t.warmth;
      acc.tension += t.tension;
      acc.hope += t.hope;
      acc.motivation += t.motivation;
      acc.intrusion += t.intrusion;
      return acc;
    },
    { valence: 0, arousal: 0, warmth: 0, tension: 0, hope: 0, motivation: 0, intrusion: 0 }
  );
  const n = tracksList.length;
  return {
    valence: sums.valence / n,
    arousal: sums.arousal / n,
    warmth: sums.warmth / n,
    tension: sums.tension / n,
    hope: sums.hope / n,
    motivation: sums.motivation / n,
    intrusion: sums.intrusion / n,
  };
}

export function getKeyDistribution(tracksList: Track[]) {
  const map: Record<string, number> = {};
  tracksList.forEach((t) => {
    const base = t.key.split(" ")[0];
    map[base] = (map[base] || 0) + 1;
  });
  return map;
}

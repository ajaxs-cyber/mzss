/* ------------------------------------------------------------------ */
/*  Client-side matching algorithm — mirrors Django views.py logic    */
/* ------------------------------------------------------------------ */

import { tracks as TRACKS, type Track } from '@/data/musicLibrary';

export interface EmotionRange {
  min: number;
  max: number;
}

export interface TargetProfile {
  valence: EmotionRange;
  arousal: EmotionRange;
  warmth: EmotionRange;
  tension: EmotionRange;
  hope: EmotionRange;
  motivation: EmotionRange;
  intrusion: EmotionRange;
  constraints: {
    allowLyrics: boolean;
    allowVocal: boolean;
    minBpm: number;
    maxBpm: number;
  };
}

export interface MatchResult {
  track: Track;
  emotionMatch: number;
  totalScore: number;
  details: Record<string, { score: number; target: string; match: number }>;
}

/**
 * Compute emotion match score for a single track against a target profile.
 * Score = weighted average of per-dimension match (range-based).
 */
export function computeEmotionMatch(
  track: Track,
  profile: TargetProfile
): { total: number; details: Record<string, { score: number; target: string; match: number }> } {
  type DimKey = 'valence' | 'arousal' | 'warmth' | 'tension' | 'hope' | 'motivation' | 'intrusion';

  const dims: Array<{ key: DimKey; weight: number }> = [
    { key: 'valence', weight: 0.25 },
    { key: 'arousal', weight: 0.20 },
    { key: 'warmth', weight: 0.15 },
    { key: 'tension', weight: 0.10 },
    { key: 'hope', weight: 0.10 },
    { key: 'motivation', weight: 0.10 },
    { key: 'intrusion', weight: 0.10 },
  ];

  let totalWeight = 0;
  let weightedMatch = 0;
  const details: Record<string, { score: number; target: string; match: number }> = {};

  for (const dim of dims) {
    const range = profile[dim.key] as EmotionRange;
    const trackVal = track[dim.key] as number;
    const halfSpan = Math.max((range.max - range.min) / 2, 0.1);

    let match: number;
    if (trackVal >= range.min && trackVal <= range.max) {
      match = 1.0;
    } else {
      const dist = trackVal < range.min ? range.min - trackVal : trackVal - range.max;
      match = Math.max(0, 1.0 - dist / (halfSpan * 2));
    }

    totalWeight += dim.weight;
    weightedMatch += match * dim.weight;
    details[dim.key] = {
      score: trackVal,
      target: `${range.min.toFixed(1)}\u2013${range.max.toFixed(1)}`,
      match: Math.round(match * 100),
    };
  }

  return {
    total: totalWeight > 0 ? weightedMatch / totalWeight : 0,
    details,
  };
}

/**
 * Run full matching: filter + score + sort.
 */
export function runMatching(profile: TargetProfile): MatchResult[] {
  const results: MatchResult[] = [];

  for (const track of TRACKS) {
    // Hard filters
    if (!profile.constraints.allowVocal && track.vocalProbability > 0.3) continue;
    if (!profile.constraints.allowLyrics && track.vocalProbability > 0.5) continue;
    if (track.bpm < profile.constraints.minBpm || track.bpm > profile.constraints.maxBpm) continue;

    // Intrusion hard cap
    if (track.intrusion > 0.8) continue;

    const { total, details } = computeEmotionMatch(track, profile);
    results.push({ track, emotionMatch: total, totalScore: total, details });
  }

  results.sort((a, b) => b.totalScore - a.totalScore);
  return results;
}

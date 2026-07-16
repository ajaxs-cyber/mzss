"""
Convert music_analysis_output.json to TypeScript musicLibrary.ts format.
"""
import json

with open("music_analysis_output.json", encoding="utf-8") as f:
    data = json.load(f)

lines = []
lines.append("""/* ------------------------------------------------------------------ */
/*  Music Library Data Layer — MZSS v2.0                               */
/*  Auto-generated from real MP3 analysis (librosa)                     */
/* ------------------------------------------------------------------ */

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
  rightsStatus: "authorized" | "restricted" | "unknown" | "disabled";
  reviewStatus: "unreviewed" | "reviewed" | "needs_review";
  commercialAllowed: boolean;
  vocalProbability: number;
  audioUrl?: string;
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
  confidence: number;
  sampleCount: number;
  fusionLambda: number;
  explanation: string[];
}

export const tracks: Track[] = [""")

for t in data["tracks"]:
    af = t["audioFeatures"]
    dur_sec = t["duration_sec"]
    mins = int(dur_sec // 60)
    secs = int(dur_sec % 60)
    duration_str = f"{mins}:{secs:02d}"

    entry = f"""  {{
    id: "{t['id']}",
    title: "{t['title']}",
    artist: "{t['artist']}",
    genre: "{t['genre']}",
    bpm: {t['bpm']},
    key: "{t['key']}",
    duration: "{duration_str}",
    durationSec: {dur_sec},
    valence: {t['valence']},
    arousal: {t['arousal']},
    warmth: {t['warmth']},
    tension: {t['tension']},
    hope: {t['hope']},
    motivation: {t['motivation']},
    intrusion: {t['intrusion']},
    tags: ["{t['genre']}"],
    cover: "",
    sceneType: "",
    lufs: "{t['lufs']:.1f} LUFS",
    lufsValue: {t['lufs']},
    rightsStatus: "authorized",
    reviewStatus: "unreviewed",
    commercialAllowed: true,
    vocalProbability: {t['audioFeatures']['vocalClarity'] / 7:.4f},
    audioUrl: "{t['audioUrl']}",
    audioFeatures: {{
      beatCv: {af['beatCv']},
      onsetRate: {af['onsetRate']},
      percussiveRatio: {af['percussiveRatio']},
      beatClarity: {af['beatClarity']},
      majorProbability: {af['majorProbability']},
      minorProbability: {af['minorProbability']},
      keyClarity: {af['keyClarity']},
      dissonance: {af['dissonance']},
      melodyRise: {af['melodyRise']},
      lra: {af['lra']},
      spikeCount: {af['spikeCount']},
      energy: {af['energy']},
      dynamicFlux: {af['dynamicFlux']},
      centroid: {af['centroid']},
      flux: {af['flux']},
      harmonicRatio: {af['harmonicRatio']},
      acousticProbability: {af['acousticProbability']},
      electronicProbability: {af['electronicProbability']},
      vocalClarity: {af['vocalClarity']},
      lyricsValence: 0,
      themeSimilarity: 50,
    }},
    confidence: 0.80,
    sampleCount: 0,
    fusionLambda: 0.70,
    explanation: {json.dumps(t['explanation'], ensure_ascii=False)},
  }}"""

    lines.append(entry)

# Join entries with commas between array elements
output = lines[0] + "\n" + ",\n".join(lines[1:]) + "\n];\n"
lines.append("")

with open("frontend/src/data/musicLibrary.ts", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Written {len(data['tracks'])} tracks to frontend/src/data/musicLibrary.ts")

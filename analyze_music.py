"""
Music Analysis Script - Extract acoustic features from MP3 files
Outputs real data to replace fake musicLibrary.ts entries.

Usage: python analyze_music.py
Output: music_analysis_output.json
"""

import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
import librosa
import librosa.display

MUSIC_DIR = Path(__file__).parent / "music_files"
OUTPUT_FILE = Path(__file__).parent / "music_analysis_output.json"

# Genre mapping based on Chinese filename suffixes
GENRE_MAP = {
    "—摇滚": "摇滚", "—轻音乐": "轻音乐", "—蓝调": "蓝调",
    "—爵士": "爵士", "—民谣": "民谣", "—R&B": "R&B",
    "—中国风": "中国风", "—KPOP": "KPOP",
}
# English filenames → genre hints
ENGLISH_HINTS = {
    "punk": "摇滚", "rock": "摇滚", "jazz": "爵士", "blues": "蓝调",
    "r&b": "R&B", "kpop": "KPOP", "folk": "民谣",
    "ambient": "氛围音乐", "electronic": "电子",
}


def guess_genre(filename: str) -> str:
    """Guess genre from filename."""
    name_lower = filename.lower()
    for suffix, genre in GENRE_MAP.items():
        if suffix in filename:
            return genre
    for hint, genre in ENGLISH_HINTS.items():
        if hint in name_lower:
            return genre
    return "轻音乐"


def guess_artist_and_title(filename: str):
    """Extract clean title from filename."""
    name = Path(filename).stem
    # Remove genre suffix
    for suffix in GENRE_MAP:
        name = name.replace(suffix, "").strip()
    # Capitalize English
    return name, ""


def derive_emotions(features: dict) -> dict:
    """
    Rule-based derivation of 7-dimension emotion scores (0-1 scale).
    Based on well-established music-psychology mappings.

    Valence: major mode + melodic rise + harmonic richness → positive
    Arousal: energy + onset density + tempo → excitement
    Warmth: acoustic timbre + harmonic structure + low dissonance
    Tension: dissonance + spectral flux + dynamic range + surprises
    Hope: major mode + ascending melody + moderate-high valence
    Motivation: drive from rhythm + percussiveness + moderate-high arousal
    Intrusion: vocal presence/clarity + high arousal + lyrical content
    """

    # Valence (0-1): major mode probability + melodic direction
    major_p = features.get("major_probability", 0.5)
    melody_rise = features.get("melody_rise", 0.5)
    harmonic_ratio = features.get("harmonic_ratio", 0.5)
    valence = 0.4 * major_p + 0.2 * melody_rise + 0.2 * harmonic_ratio + 0.2 * 0.5
    valence = np.clip(valence * 0.8 + 0.2, 0.05, 0.95)  # Scale to reasonable range

    # Arousal (0-1): energy + onset rate + tempo
    energy = features.get("energy", 0.5)
    onset_rate_norm = np.clip(features.get("onset_rate", 4.0) / 10.0, 0.0, 1.0)
    bpm_norm = np.clip(features.get("bpm", 120) / 180.0, 0.1, 1.0)
    arousal = 0.4 * energy + 0.3 * onset_rate_norm + 0.2 * bpm_norm + 0.1 * 0.5
    arousal = np.clip(arousal, 0.05, 0.95)

    # Warmth (0-1): acoustic timbre + harmonic + low dissonance
    acoustic_p = features.get("acoustic_probability", 0.5)
    dissonance = features.get("dissonance", 0.3)
    warmth = 0.5 * acoustic_p + 0.3 * (1.0 - dissonance) + 0.2 * harmonic_ratio
    warmth = np.clip(warmth * 0.85 + 0.15, 0.05, 0.95)

    # Tension (0-1): dissonance + flux + dynamic range + spikes
    flux_norm = np.clip(features.get("flux", 0.3) / 0.8, 0.0, 1.0)
    lra_norm = np.clip(features.get("lra", 8.0) / 25.0, 0.0, 1.0)
    spike_norm = np.clip(features.get("spike_count", 5) / 30.0, 0.0, 1.0)
    tension = 0.35 * dissonance + 0.25 * flux_norm + 0.2 * lra_norm + 0.2 * spike_norm
    tension = np.clip(tension, 0.02, 0.95)

    # Hope (0-1): major probability + melody rise + valence contribution
    hope = 0.4 * major_p + 0.3 * melody_rise + 0.3 * valence
    hope = np.clip(hope * 0.9 + 0.05, 0.05, 0.95)

    # Motivation (0-1): percussive + tempo + arousal
    percussive = features.get("percussive_ratio", 0.3)
    motivation = 0.3 * percussive + 0.3 * bpm_norm + 0.4 * arousal
    motivation = np.clip(motivation, 0.05, 0.95)

    # Intrusion (0-1): vocal clarity + vocal probability + arousal effect
    vocal_clarity_norm = np.clip(features.get("vocal_clarity", 3) / 7.0, 0.0, 1.0)
    vocal_prob = features.get("vocal_probability", 0.0)
    intrusion = 0.4 * vocal_clarity_norm + 0.35 * vocal_prob + 0.25 * arousal
    intrusion = np.clip(intrusion, 0.02, 0.90)

    return {
        "valence": round(float(valence), 4),
        "arousal": round(float(arousal), 4),
        "warmth": round(float(warmth), 4),
        "tension": round(float(tension), 4),
        "hope": round(float(hope), 4),
        "motivation": round(float(motivation), 4),
        "intrusion": round(float(intrusion), 4),
    }


def analyze_file(filepath: Path) -> dict | None:
    """Extract acoustic features from a single MP3 file."""
    try:
        print(f"  Analyzing: {filepath.name}")
        y, sr = librosa.load(str(filepath), sr=22050, duration=120)

        if len(y) < sr * 5:
            print(f"    SKIPPED: too short ({len(y)/sr:.1f}s)")
            return None

        dur_sec = len(y) / sr
        y_harm, y_perc = librosa.effects.hpss(y)

        # ── Tempo & Beat ──
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)

        beat_frames = librosa.frames_to_time(beats, sr=sr)
        if len(beat_frames) > 2:
            beat_intervals = np.diff(beat_frames)
            beat_cv = float(np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-8))
            beat_cv = min(beat_cv, 1.0)
        else:
            beat_cv = 0.3

        # ── Onsets ──
        onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        onset_rate = len(onset_times) / dur_sec

        # ── Percussive Ratio ──
        percussive_ratio = float(np.sum(y_perc ** 2) / (np.sum(y ** 2) + 1e-8))

        # ── Beat Clarity ──
        onset_acf = librosa.autocorrelate(onset_env)
        beat_clarity = float(np.max(onset_acf[1:]) / (np.max(onset_acf) + 1e-8))
        beat_clarity = np.clip(beat_clarity, 0.0, 1.0)

        # ── Spectral Features ──
        S = np.abs(librosa.stft(y, n_fft=2048))
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        centroid = float(np.average(freqs, weights=np.mean(S, axis=1)))
        centroid_norm = centroid / (sr / 2)

        flux_raw = np.mean(np.abs(np.diff(S, axis=1))) / (np.mean(np.abs(S)) + 1e-8)
        flux = float(np.clip(flux_raw * 1.5, 0.0, 1.0))

        # ── Chroma / Key ──
        chroma = librosa.feature.chroma_stft(y=y_harm, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) / 7.0
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]) / 7.0
        major_corr = np.max([np.corrcoef(chroma_mean, np.roll(major_profile, i))[0, 1] for i in range(12)])
        minor_corr = np.max([np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0, 1] for i in range(12)])

        major_corr = max(major_corr, 0.0)
        minor_corr = max(minor_corr, 0.0)
        total_corr = major_corr + minor_corr
        if total_corr > 0:
            major_probability = major_corr / total_corr
            minor_probability = minor_corr / total_corr
        else:
            major_probability = 0.5
            minor_probability = 0.5

        key_clarity = float(np.clip(total_corr * 0.8, 0.1, 1.0))

        # ── Energy / Loudness ──
        rms = librosa.feature.rms(y=y)[0]
        # Use percentile-based normalization: reference = average of pop music
        energy_raw = np.mean(rms)
        energy = float(np.clip(energy_raw / (np.percentile(rms, 95) + 1e-8) * 0.6 + np.clip(energy_raw * 6, 0.0, 0.7), 0.02, 0.98))
        lufs_approx = float(20 * np.log10(np.mean(rms) + 1e-8))

        # LRA approximated from RMS variation
        rms_db = 20 * np.log10(rms + 1e-8)
        rms_db = rms_db[rms_db > -60]
        if len(rms_db) > 10:
            p10 = np.percentile(rms_db, 10)
            p90 = np.percentile(rms_db, 90)
            lra = float(p90 - p10)
        else:
            lra = 8.0

        # Spike count
        rms_diff = np.diff(rms)
        spike_threshold = np.mean(rms_diff) + 3 * np.std(rms_diff)
        spike_count = float(np.sum(rms_diff > spike_threshold) / dur_sec * 30)

        # Dynamic flux
        dynamic_flux = float(np.std(rms) / (np.mean(rms) + 1e-8))
        dynamic_flux = np.clip(dynamic_flux * 2, 0.0, 1.0)

        # ── Harmonic Ratio ──
        harmonic_ratio = float(np.sum(y_harm ** 2) / (np.sum(y ** 2) + 1e-8))

        # ── Acoustic/Electronic probability ──
        # Acoustic = high harmonic ratio + low spectral centroid
        centroid_factor = np.clip(1.0 - centroid_norm * 1.5, 0.0, 1.0)
        acoustic_probability = float(0.6 * harmonic_ratio + 0.4 * centroid_factor)
        electronic_probability = 1.0 - acoustic_probability

        # ── Dissonance ──
        # Use spectral contrast between peaks and valleys as roughness proxy
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr).mean(axis=1)
        dissonance = float(np.clip(np.mean(contrast[2:4]) / 40.0, 0.02, 0.95))

        # ── Melody Rise ──
        pitch_track = librosa.yin(y, fmin=80, fmax=2000, sr=sr)
        pitch_track = pitch_track[np.isfinite(pitch_track)]
        if len(pitch_track) > 100:
            half = len(pitch_track) // 2
            first_half = np.mean(pitch_track[:half])
            second_half = np.mean(pitch_track[half:])
            if first_half > 0:
                slope = (second_half - first_half) / first_half
                melody_rise = float(np.clip(slope + 0.3, 0.0, 1.0) * 2.0)
            else:
                melody_rise = 0.5
        else:
            melody_rise = 0.5
        melody_rise = np.clip(melody_rise, 0.0, 1.0)

        # ── Vocal Probability ──
        # High centroid in 300-3000Hz region suggests vocals
        voc_band = (freqs >= 300) & (freqs <= 3000)
        if np.any(voc_band):
            vocal_energy = np.sum(np.mean(S[voc_band], axis=1)) / (np.sum(np.mean(S, axis=1)) + 1e-8)
        else:
            vocal_energy = 0.3
        vocal_probability = float(np.clip(vocal_energy * 2.0 - 0.3, 0.0, 1.0))

        # Vocal clarity: how concentrated energy is in vocal range
        vocal_clarity = float(np.clip(vocal_energy * 3.5, 1.0, 7.0))

        # ── Spectral flux ──
        flux_val = float(np.clip(np.mean(np.abs(np.diff(S, axis=1))) / (np.mean(S) + 1e-8), 0.0, 1.0))

        # ── Assemble features ──
        features = {
            "bpm": round(bpm, 1),
            "beat_cv": round(beat_cv, 4),
            "onset_rate": round(onset_rate, 2),
            "percussive_ratio": round(percussive_ratio, 4),
            "beat_clarity": round(beat_clarity, 4),
            "major_probability": round(major_probability, 4),
            "minor_probability": round(minor_probability, 4),
            "key_clarity": round(key_clarity, 4),
            "dissonance": round(dissonance, 4),
            "melody_rise": round(melody_rise, 4),
            "lufs": round(lufs_approx, 1),
            "lra": round(lra, 1),
            "spike_count": round(spike_count, 1),
            "energy": round(energy, 4),
            "dynamic_flux": round(dynamic_flux, 4),
            "centroid": round(centroid, 0),
            "flux": round(flux, 4),
            "harmonic_ratio": round(harmonic_ratio, 4),
            "acoustic_probability": round(acoustic_probability, 4),
            "electronic_probability": round(electronic_probability, 4),
            "vocal_probability": round(vocal_probability, 4),
            "vocal_clarity": round(vocal_clarity, 1),
            "duration_sec": round(dur_sec, 1),
        }

        emotions = derive_emotions(features)
        features.update(emotions)

        # Key signature estimate
        key_names = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
        key_idx = int(np.argmax(chroma_mean))
        key_sig = f"{key_names[key_idx]} {'major' if major_probability > minor_probability else 'minor'}"
        features["key"] = key_sig

        return features

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def generate_explanation(features: dict, genre: str) -> list[str]:
    """Generate interpretable explanation lines for a track."""
    lines = []

    major_p = features.get("major_probability", 0.5)
    valence = features.get("valence", 0.5)
    energy = features.get("energy", 0.5)
    acoustic = features.get("acoustic_probability", 0.5)
    dissonance = features.get("dissonance", 0.3)
    vocal_prob = features.get("vocal_probability", 0.0)
    bpm = features.get("bpm", 100)

    if major_p > 0.65:
        lines.append(f"大调主导({major_p:.2f})带来积极明亮的基调")
    elif major_p < 0.35:
        lines.append(f"小调主导({1-major_p:.2f})营造深沉情绪色彩")

    if energy > 0.7:
        lines.append(f"高能量({energy:.2f})配合密集节拍产生强烈律动感")
    elif energy < 0.3:
        lines.append(f"低能量({energy:.2f})营造松弛沉静的聆听体验")

    if acoustic > 0.7:
        lines.append(f"高原声乐器占比({acoustic:.2f})带来{features.get('warmth', 0.5):.2f}的温暖感")
    else:
        lines.append(f"电子音色主导({1-acoustic:.2f})呈现现代数字质感")

    if dissonance < 0.15:
        lines.append(f"极低不协和度({dissonance:.2f})确保听感舒适无干扰")
    elif dissonance > 0.5:
        lines.append(f"较高不协和度({dissonance:.2f})制造独特张力与戏剧感")

    if vocal_prob < 0.15:
        lines.append("纯器乐作品，无歌词不干扰阅读专注力")
    elif vocal_prob > 0.6:
        lines.append(f"明确人声存在({vocal_prob:.2f})增强情感叙事表达")

    if not lines:
        lines.append(f"均衡配器与{BPM:.0f}BPM的中性节奏适合多场景使用")

    return lines


def main():
    mp3_files = sorted(MUSIC_DIR.glob("*.mp3"))
    if not mp3_files:
        print(f"No MP3 files found in {MUSIC_DIR}")
        sys.exit(1)

    print(f"Found {len(mp3_files)} MP3 files\n")

    results = []
    for i, mp3_path in enumerate(mp3_files):
        print(f"[{i+1}/{len(mp3_files)}]", end=" ")
        features = analyze_file(mp3_path)
        if features is None:
            continue

        genre = guess_genre(mp3_path.name)
        artist, title_clean = guess_artist_and_title(mp3_path.name)
        title = title_clean or mp3_path.stem

        # Audio URL from GitHub raw
        audio_url = f"https://raw.githubusercontent.com/ajaxs-cyber/my-music-storage/main/{mp3_path.name}"

        entry = {
            "id": f"track-{len(results)+1:03d}",
            "title": title,
            "artist": artist or "未知艺术家",
            "genre": genre,
            "bpm": features["bpm"],
            "key": features.get("key", "?"),
            "duration_sec": features["duration_sec"],
            "lufs": features["lufs"],
            "audioUrl": audio_url,
            # 7-dimension emotions
            "valence": features["valence"],
            "arousal": features["arousal"],
            "warmth": features["warmth"],
            "tension": features["tension"],
            "hope": features["hope"],
            "motivation": features["motivation"],
            "intrusion": features["intrusion"],
            # Full audio features
            "audioFeatures": {
                "beatCv": features["beat_cv"],
                "onsetRate": features["onset_rate"],
                "percussiveRatio": features["percussive_ratio"],
                "beatClarity": features["beat_clarity"],
                "majorProbability": features["major_probability"],
                "minorProbability": features["minor_probability"],
                "keyClarity": features["key_clarity"],
                "dissonance": features["dissonance"],
                "melodyRise": features["melody_rise"],
                "lra": features["lra"],
                "spikeCount": features["spike_count"],
                "energy": features["energy"],
                "dynamicFlux": features["dynamic_flux"],
                "centroid": features["centroid"],
                "flux": features["flux"],
                "harmonicRatio": features["harmonic_ratio"],
                "acousticProbability": features["acoustic_probability"],
                "electronicProbability": features["electronic_probability"],
                "vocalClarity": features["vocal_clarity"],
                "lyricsValence": 0.0,
                "themeSimilarity": 50.0,
            },
            "confidence": 0.80,
            "sampleCount": 0,
            "fusionLambda": 0.70,
            "explanation": generate_explanation(features, genre),
        }
        results.append(entry)

    output = {"tracks": results, "total": len(results)}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(results)} tracks analyzed → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

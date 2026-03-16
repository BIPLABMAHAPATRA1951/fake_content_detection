"""
audio_detector.py - Calibrated against real data
Real voice features: flatness=0.061, mfcc_var=2677, rms_cv=0.705
gTTS features:       flatness=0.026, mfcc_var=1389, rms_cv=0.645
"""

def analyze_audio(audio_file) -> tuple:
    try:
        import numpy as np
        import librosa
        import io

        audio_bytes = audio_file.read()
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050, mono=True)

        if len(y) < sr * 0.5:
            return 0.5, "Audio too short to analyze"

        signals = []
        score = 0.0

        # 1. MFCC variance — strongest signal
        # Real: ~2677, TTS: ~1389
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_var = float(np.mean(np.var(mfccs, axis=1)))
        if mfcc_var < 1600:
            score += 0.45
            signals.append(f"low MFCC variance ({mfcc_var:.0f}) — synthetic speech")
        elif mfcc_var < 2000:
            score += 0.2
            signals.append(f"moderate MFCC variance ({mfcc_var:.0f}) — possibly synthetic")

        # 2. Spectral flatness
        # Real: ~0.061, TTS: ~0.026
        flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
        if flatness < 0.035:
            score += 0.3
            signals.append(f"low spectral flatness ({flatness:.3f}) — TTS pattern")
        elif flatness < 0.045:
            score += 0.1
            signals.append(f"moderate flatness ({flatness:.3f})")

        # 3. RMS consistency
        # Real: ~0.705, TTS: ~0.645
        rms = librosa.feature.rms(y=y)[0]
        rms_cv = float(np.std(rms)) / (float(np.mean(rms)) + 1e-6)
        if rms_cv < 0.65:
            score += 0.15
            signals.append(f"steady volume (cv={rms_cv:.2f}) — unnatural consistency")
        elif rms_cv < 0.68:
            score += 0.05
            signals.append(f"somewhat steady volume (cv={rms_cv:.2f})")

        # 4. Pitch std
        # Real: ~243, TTS: ~210
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_vals = pitches[magnitudes > np.max(magnitudes) * 0.15]
        if len(pitch_vals) > 10:
            pitch_std = float(np.std(pitch_vals))
            if pitch_std < 220:
                score += 0.1
                signals.append(f"consistent pitch (std={pitch_std:.0f})")

        final_score = min(score, 1.0)
        explanation = " | ".join(signals) if signals else "Natural audio — no synthetic signals detected"
        return final_score, explanation

    except ImportError:
        return 0.5, "librosa not installed"
    except Exception as e:
        return 0.5, f"Audio analysis error: {e}"

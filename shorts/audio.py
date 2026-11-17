"""숏폼용 배경음악과 효과음을 직접 만들어 WAV로 저장한다.

외부 음원을 쓰지 않고 수학적으로 소리를 합성하므로 저작권 걱정이 없다.
"""

import wave

import numpy as np

SR = 44100
BPM = 104
BEAT = 60 / BPM

# 영상마다 조금씩 다른 코드 진행 (음 이름은 MIDI 번호)
PROGRESSIONS = [
    [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)],  # C  G  Am F
    [(57, 60, 64), (53, 57, 60), (60, 64, 67), (55, 59, 62)],  # Am F  C  G
    [(53, 57, 60), (55, 59, 62), (52, 55, 59), (57, 60, 64)],  # F  G  Em Am
    [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)],  # C  Am F  G
    [(62, 65, 69), (55, 59, 62), (60, 64, 67), (57, 60, 64)],  # Dm G  C  Am
]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def tone(freq, dur, decay=None, harmonics=(1.0,), detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    sig = sum(a * np.sin(2 * np.pi * freq * (k + 1) * (1 + detune) * t)
              for k, a in enumerate(harmonics))
    if decay:
        sig *= np.exp(-t / decay)
    return sig


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def soft_env(n, attack, release):
    env = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] *= np.linspace(1, 0, r)
    return env


def music(total, variant):
    n = int(total * SR)
    left, right = np.zeros(n), np.zeros(n)
    prog = PROGRESSIONS[variant % len(PROGRESSIONS)]
    bar = BEAT * 4
    rng = np.random.default_rng(variant)

    t_bar = 0.0
    ci = 0
    while t_bar < total:
        chord = prog[ci % len(prog)]
        # 패드: 은은하게 깔리는 화음 (좌우를 살짝 다르게 해서 넓게)
        for note in chord:
            for det, ch in ((-0.002, left), (0.002, right)):
                s = tone(hz(note), bar, harmonics=(1.0, 0.25, 0.08), detune=det)
                s *= soft_env(len(s), 0.06, 0.08)
                add(ch, s, t_bar, 0.045)
        # 베이스: 1, 3박
        for b in (0, 2):
            s = tone(hz(chord[0] - 24), BEAT * 1.8, decay=0.5, harmonics=(1.0, 0.35))
            s *= soft_env(len(s), 0.01, 0.1)
            add(left, s, t_bar + b * BEAT, 0.22)
            add(right, s, t_bar + b * BEAT, 0.22)
        # 아르페지오: 8분음표로 반짝이는 멜로디
        arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        for k in range(8):
            s = tone(hz(arp[k % 4]), BEAT, decay=0.18, harmonics=(1.0, 0.4, 0.15))
            s *= soft_env(len(s), 0.004, 0.05)
            pan = 0.35 if k % 2 else 0.65
            add(left, s, t_bar + k * BEAT / 2, 0.07 * (1 - pan) * 2)
            add(right, s, t_bar + k * BEAT / 2, 0.07 * pan * 2)
        # 드럼: 킥(매 박), 하이햇(엇박), 클랩(2·4박)
        for b in range(4):
            tb = t_bar + b * BEAT
            kt = np.arange(int(0.35 * SR)) / SR
            kick = np.sin(2 * np.pi * (48 * kt + 90 * 0.04 * (1 - np.exp(-kt / 0.04))))
            kick *= np.exp(-kt / 0.12)
            add(left, kick, tb, 0.34)
            add(right, kick, tb, 0.34)
            hat = np.diff(rng.standard_normal(int(0.05 * SR) + 1))
            hat *= np.exp(-np.arange(len(hat)) / SR / 0.012)
            add(left, hat, tb + BEAT / 2, 0.035)
            add(right, hat, tb + BEAT / 2, 0.045)
            if b in (1, 3):
                clap = rng.standard_normal(int(0.15 * SR))
                clap = np.convolve(clap, np.ones(3) / 3, mode="same")
                clap *= np.exp(-np.arange(len(clap)) / SR / 0.05)
                add(left, clap, tb, 0.06)
                add(right, clap, tb, 0.06)
        t_bar += bar
        ci += 1
    return left, right


def whoosh(dur=0.55):
    """장면 전환 '휙' 소리: 잡음의 밝기가 점점 올라갔다 내려간다."""
    n = int(dur * SR)
    noise = np.random.default_rng(1).standard_normal(n + 2048)
    out = np.zeros(n + 2048)
    size, hop = 1024, 512
    win = np.hanning(size)
    freqs = np.fft.rfftfreq(size, 1 / SR)
    for start in range(0, n, hop):
        p = start / n
        center = 300 + 4500 * np.sin(np.pi * p) ** 2
        mask = np.exp(-((freqs - center) / (center * 0.6)) ** 2)
        seg = np.fft.irfft(np.fft.rfft(noise[start:start + size] * win) * mask, size)
        out[start:start + size] += seg
    out = out[:n]
    out *= np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out / (np.abs(out).max() + 1e-9)


def ding():
    """강조할 때 나는 '띵' 종소리."""
    s = (tone(hz(88), 1.2, decay=0.35, harmonics=(1.0, 0.0, 0.3))
         + 0.6 * tone(hz(95), 1.2, decay=0.25))
    return s * soft_env(len(s), 0.003, 0.1) / 1.6


def make_audio(path, total, scene_starts, ding_times, variant):
    left, right = music(total, variant)
    w, d = whoosh(), ding()
    for t in scene_starts[1:]:
        add(left, w, max(0, t - 0.2), 0.22)
        add(right, w, max(0, t - 0.2), 0.22)
    for t in ding_times:
        add(left, d, t, 0.32)
        add(right, d, t, 0.32)

    st = np.stack([left, right], axis=1)
    fade_in, fade_out = int(0.3 * SR), int(1.2 * SR)
    st[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    st[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    st = np.tanh(st * 1.2)  # 부드러운 리미터
    st *= 0.89 / (np.abs(st).max() + 1e-9)

    pcm = (st * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())

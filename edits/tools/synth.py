# Original royalty-free beats synthesized from scratch, locked to each edit's BPM grid.
import numpy as np, soundfile as sf, sys
from scipy.signal import butter, sosfilt, fftconvolve
SR = 44100
rng = np.random.default_rng(7)
def n2f(n): return 440.0 * 2 ** ((n - 69) / 12)
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.exp(-t / d); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x)
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += g * x[: j - i]
def kick(f0=150, f1=45, d=0.35):
    n = int(d * 1.5 * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.04); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(2.2 * np.sin(ph) * env(n, 0.001, d))
def clap(d=0.18):
    n = int(0.4 * SR); x = rng.standard_normal(n); e = np.zeros(n)
    for o in (0, .01, .02): e += env(n, 0.001, 0.008) * (np.arange(n) >= o * SR)
    e[int(.02 * SR):] += env(n - int(.02 * SR), 0.001, d) * 0.7
    return filt(x * e, 'bandpass', [900, 6000]) * 0.8
def hat(d=0.03, open_=False):
    n = int((0.3 if open_ else 0.08) * SR); x = rng.standard_normal(n)
    return filt(x * env(n, 0.0005, 0.12 if open_ else d), 'highpass', 7000) * 0.5
def bells(d=0.12):  # sleigh-bell jingle
    n = int(0.25 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in rng.uniform(5000, 11000, 9): x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    x += rng.standard_normal(n) * 1.5
    return filt(x * env(n, 0.001, d), 'highpass', 4500) * 0.18
def tone(f, d, harm=(1, .5, .25), dec=0.4, a=0.003, vib=0):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    fm = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t))
    for k, h in enumerate(harm, 1): x += h * np.sin(2 * np.pi * np.cumsum(fm * k) / SR)
    return x * env(n, a, dec)
def glock(f, d=0.6): return tone(f, d, (1, 0, .3, 0, 0, .15), 0.35) * 0.25
def pluck(f, d=0.5):  # Karplus-Strong piano-ish pluck
    N = int(SR / f); buf = rng.uniform(-1, 1, N); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % N]; buf[i % N] = 0.497 * (buf[i % N] + buf[(i + 1) % N])
    return out * 0.35
def pad(fs, d, bright=2500):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in fs:
        for det in (-0.12, 0, 0.12):
            ph = (f * 2 ** (det / 12) * t + rng.uniform()) % 1.0; x += (2 * ph - 1)
    x = filt(x, 'lowpass', bright); e = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.1).clip(0)
    return x * e / (len(fs) * 3) * 0.6
def bass808(f, d, glide_from=None):
    n = int(d * SR); t = np.arange(n) / SR
    ff = np.full(n, f) if glide_from is None else f + (glide_from - f) * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(ff) / SR); x = np.tanh(2.5 * x) * env(n, 0.002, d * 0.9)
    return x * 0.55
def riser(d):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        fc = 400 + 9000 * (i / n) ** 2; out[i:i + seg] = filt(x[i:i + seg], 'bandpass', [fc * .7, min(fc * 1.3, 20000)])
    return out * (t / d) ** 2 * 0.35
def impact():
    n = int(1.5 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (40 + 60 * np.exp(-t / .1)) * t) * env(n, .001, .5) * .8 +
            filt(rng.standard_normal(n), 'lowpass', 3000) * env(n, .001, .25) * .4)
def reverb(x, wet=0.18, dec=1.2):
    n = int(dec * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (dec / 5))
    ir = filt(ir, 'lowpass', 6000); y = fftconvolve(x, ir)[: len(x)]
    return x + wet * y / (np.abs(y).max() + 1e-9) * np.abs(x).max()
def finish(L, R, tail_from):
    st = np.stack([L, R], 1)
    i = int(tail_from * SR); fade = np.linspace(1, 0, len(st) - i) ** 1.5; st[i:] *= fade[:, None]
    st = np.tanh(st / (np.abs(st).max() + 1e-9) * 1.6) ; return st / np.abs(st).max() * 0.89

def track_gift(beats, bpm=150):
    """Cozy festive pop @150 (half-time feel): sleigh bells, glockenspiel, piano pluck, snaps."""
    b = 60 / bpm; T = beats * b + 1.5; n = int(T * SR); dr = np.zeros(n); mu = np.zeros(n)
    prog = [(67, 71, 74), (64, 67, 71), (60, 64, 67), (62, 66, 69)]  # G  Em  C  D
    mel = [79, 78, 76, 74, 76, 78, 79, 83]
    for i in range(beats):
        t = i * b; bar = (i // 8) % 4
        if i % 4 == 0: add(dr, kick(120, 50, .3), t, .9)
        if i % 4 == 2: add(dr, clap(.12), t, .7)
        if i % 8 == 7: add(dr, kick(120, 50, .3), t + b / 2, .6)
        add(dr, bells(.09 if i % 2 else .15), t, .9 if i % 2 == 0 else .55)
        add(dr, bells(.06), t + b / 2, .35)
        if i % 8 == 0: add(mu, pad([n2f(x) for x in prog[bar]], 8 * b, 1800), t, .9)
        if i % 2 == 0: add(mu, pluck(n2f(prog[bar][(i // 2) % 3] - 12) ), t, .9)
        if i >= 4 and i % 2 == 0: add(mu, glock(n2f(mel[(i // 2) % 8])), t, 1)
        if i % 8 == 0: add(mu, tone(n2f(prog[bar][0] - 24), 8 * b, (1, .3), 4 * b), t, .35)
    add(dr, kick(120, 50, .5), beats * b, 1); add(mu, glock(n2f(91), 1.4), beats * b, 1.2)
    mu = reverb(mu, .3, 1.8); x = dr + mu
    return finish(x + .02 * np.roll(mu, 300), x + .02 * np.roll(mu, -300), beats * b)

def track_pov(beats, drop, bpm=133):
    """Dark-pop/trap @133: filtered build, riser, hard drop with 808 + icy pluck hook."""
    b = 60 / bpm; T = beats * b + 1.8; n = int(T * SR); dr = np.zeros(n); mu = np.zeros(n)
    roots = [53, 53, 49, 48]  # F F Db C  (F minor)
    chords = [(65, 68, 72), (65, 68, 72), (61, 65, 68), (60, 64, 67)]
    hook = [77, 0, 75, 72, 0, 72, 75, 77]
    for i in range(beats):
        t = i * b; bar = (i // 4) % 4; post = i >= drop
        if i % 4 == 0: add(mu, pad([n2f(c) for c in chords[bar]], 4 * b, 4000 if post else 900), t, .8)
        for s in range(2):
            add(mu, pluck(n2f(hook[(i * 2 + s) % 8] or 72) * (2 if post else 1), .25), t + s * b / 2,
                (.5 if post else .25) if hook[(i * 2 + s) % 8] else 0)
        if not post:
            if i % 2 == 0: add(dr, kick(140, 48, .25), t, .55 if i < drop - 4 else .0)
            add(dr, hat(), t + b / 2, .4)
        else:
            if i % 4 in (0,) or (i % 4 == 2 and i % 8 == 6): add(dr, kick(160, 45, .3), t, 1)
            if i % 4 == 0: add(mu, bass808(n2f(roots[bar] - 12), 4 * b, n2f(roots[bar])), t, 1)
            if i % 4 == 2: add(dr, clap(.2), t, .9)
            for s in range(4 if i % 4 != 3 else 6): add(dr, hat(.02), t + s * b / (4 if i % 4 != 3 else 6), .45)
    for k in range(8): add(dr, clap(.06), (drop - 2) * b + k * b / 4, .15 + .08 * k)
    add(mu, riser(4 * b), (drop - 4) * b, 1)
    gap = int((drop * b - b / 4) * SR); dr[gap:int(drop * b * SR)] *= 0.05; mu[gap:int(drop * b * SR)] *= 0.2
    add(dr, impact(), drop * b, 1.1); add(dr, impact(), beats * b, .9)
    mu = reverb(mu, .22, 1.4); x = dr + mu
    return finish(x + .03 * np.roll(mu, 250), x + .03 * np.roll(mu, -250), beats * b)

def track_reveal(beats, bpm=107):
    """Bright 80s-style synth-pop @107: drum machine, gated snare, synth-bell lead, warm pad."""
    b = 60 / bpm; T = beats * b + 1.8; n = int(T * SR); dr = np.zeros(n); mu = np.zeros(n)
    prog = [(64, 68, 71), (61, 64, 68), (66, 69, 73), (59, 63, 66)]  # E  C#m  F#m  B
    lead = [76, 75, 73, 71, 73, 71, 68, 71]
    for i in range(beats):
        t = i * b; bar = (i // 4) % 4
        add(dr, kick(130, 50, .28), t, .85 if i % 2 == 0 else .55)
        if i % 2 == 1: add(dr, reverb(clap(.25), .5, .3), t, .85)
        for s in range(2): add(dr, hat(.025), t + s * b / 2, .4 if s else .25)
        if i % 4 == 0: add(mu, pad([n2f(x) for x in prog[bar]], 4 * b, 3200), t, 1)
        for s in range(2): add(mu, tone(n2f(prog[bar][0] - 24), b / 2, (1, .6, .3), .12), t + s * b / 2, .5)
        if i >= 2: add(mu, tone(n2f(lead[i % 8]), b * .95, (1, 0, .4, 0, .2), .3, vib=.004), t, .2)
    add(dr, kick(130, 50, .6), beats * b, 1); add(mu, pad([n2f(x) for x in prog[0]], 1.6), beats * b, 1)
    mu = reverb(mu, .3, 1.6); x = dr + mu
    return finish(x + .03 * np.roll(mu, 350), x + .03 * np.roll(mu, -350), beats * b)

out = sys.argv[1]
sf.write(f"{out}/beat_v1_gift_150bpm.wav", track_gift(28), SR)
sf.write(f"{out}/beat_v2_pov_133bpm.wav", track_pov(26, 16), SR)
sf.write(f"{out}/beat_v3_reveal_107bpm.wav", track_reveal(24), SR)
print("ok")

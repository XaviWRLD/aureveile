"""Native-style Meta retargeting ads for myHeatedGloves from the real product footage.
Looks like an organic Reel (small native text, phone footage, no end card), royalty-free beat.
python3 gloves_native_ads.py [name ...]"""
import subprocess, sys, os, re
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render, FT

U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
W0, W1, W2 = U + "b20696f0-VID-20261112-WA0000.mp4", U + "bed81630-VID-20261112-WA0001.mp4", U + "3727053c-VID-20261112-WA0002.mp4"
BEATS = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/na/"
TMP = BEATS + "ov/"
OUTD = "/home/user/aureveile/edits/native_ads/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
TRACK = {"gift": ("beat_v1_gift_150bpm.wav", 60 / 150), "pov": ("beat_v2_pov_133bpm.wav", 60 / 133), "reveal": ("beat_v3_reveal_107bpm.wav", 60 / 107)}
FB = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 50)
FS = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 34)

def bubble(q, path):
    """Comment-reply sticker like the native 'Reply to comment' look (no fake names)."""
    w = int(max(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(q, font=FB), 480)) + 80
    im = Image.new("RGBA", (1080, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x0 = (1080 - w) // 2
    d.rounded_rectangle([x0 + 4, 10, x0 + w + 4, 176], 34, fill=(0, 0, 0, 70))
    d.rounded_rectangle([x0, 4, x0 + w, 170], 34, fill=(255, 255, 255, 250))
    d.text((x0 + 40, 26), "Most asked question 💬".replace(" 💬", ""), font=FS, fill=(110, 110, 110))
    d.text((x0 + 40, 80), q, font=FB, fill=(20, 20, 20))
    im.save(path); return path

# name: track, shots [(file, src start, beats)], overlays [(kind, lines, y, start_shot, end_shot)]
ADS = {
 "A_StillThinking": dict(track="gift",
    shots=[(W1, 5.5, 6), (W1, 6.6, 6), (W1, 9.5, 5), (W1, 11.5, 7), (W2, 11.5, 6)],
    ov=[("t", ["Still thinking about", "the heated gloves? 🧤"], 230, 0, 5),
        ("t", ["One click. 3 heat levels 🔥"], 1450, 0, 2),
        ("t", ["3× AA per glove, no charging 🔋"], 1450, 2, 3),
        ("t", ["Free shipping 📦"], 1450, 3, 4),
        ("t", ["1 pair $54.95 · 2 pairs $89.95", "Tap Shop Now 👇"], 1400, 4, 5)]),
 "B_DoTheyGetWarm": dict(track="reveal",
    shots=[(W0, 5.4, 4), (W0, 8.6, 4), (W1, 9.4, 4), (W2, 7.6, 4), (W2, 11.5, 5)],
    ov=[("b", "Do they actually get warm?", 230, 0, 5),
        ("t", ["Yes. Press the button,", "pick 1 of 3 heat levels 🔥"], 1400, 1, 3),
        ("t", ["Runs on 3× AA per glove.", "No charging, just swap & go 🔋"], 1400, 3, 4),
        ("t", ["1 pair $54.95 · 2 pairs $89.95", "Free shipping · Tap Shop Now 👇"], 1400, 4, 5)]),
 "C_AlwaysCold_Gift": dict(track="pov",
    shots=[(W2, 1.6, 5), (W2, 4.0, 5), (W1, 13.3, 4), (W1, 12.5, 5), (W2, 11.3, 7)],
    ov=[("t", ["For the person who's", "ALWAYS cold 🥶🎁"], 230, 0, 5),
        ("t", ["Heated gloves with 3 heat levels 🔥"], 1450, 1, 3),
        ("t", ["2 pairs $89.95", "one for them, one for you 🧤🧤"], 1400, 3, 4),
        ("t", ["Free shipping · Tap Shop Now 👇"], 1450, 4, 5)]),
 "D_POV_Commute": dict(track="gift",
    shots=[(W1, 11.4, 6), (W1, 12.6, 6), (W2, 7.5, 6), (W2, 11.5, 6), (W0, 8.6, 6)],
    ov=[("t", ["POV: your hands are finally", "warm on the way to work ☕️"], 230, 0, 5),
        ("t", ["One click before you leave 🔥"], 1450, 0, 2),
        ("t", ["3 heat levels · runs on AA batteries"], 1450, 2, 4),
        ("t", ["1 pair $54.95 · 2 pairs $89.95", "Tap Shop Now 👇"], 1400, 4, 5)]),
}

def build(name, cfg, gain, out):
    wav, ibi = TRACK[cfg["track"]]
    ins = [f for f, _, _ in cfg["shots"]]; fc = []; cuts = [0.0]; t = 0.0; labels = []
    for i, (f, s0, nb) in enumerate(cfg["shots"]):
        d = nb * ibi
        fc.append(f"[{i}:v]trim={s0}:{s0 + d:.3f},setpts=PTS-STARTPTS,fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        labels.append(f"[c{i}]"); t += d; cuts.append(t)
    total = t
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0,eq=contrast=1.02:saturation=1.03[v0]")
    cur = "[v0]"; extra = []; n = len(ins)
    for j, (kind, lines, y, a, b) in enumerate(cfg["ov"]):
        p = TMP + f"{name}_{j}.png"
        bubble(lines, p) if kind == "b" else render(lines, p)
        t0, t1 = cuts[a] + (0.12 if a else 0), cuts[b]
        extra += ["-loop", "1", "-i", p]
        fc.append(f"{cur}[{n+j}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1 - 0.034:.3f})'[o{j}]")
        cur = f"[o{j}]"
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    fc.append(f"[{n+len(cfg['ov'])}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={total-0.4:.3f}:d=0.4,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    args = sum([["-i", f] for f in ins], []) + extra + ["-i", BEATS + wav]
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "17", "-maxrate", "10M", "-bufsize", "20M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", out],
        capture_output=True, text=True)
    if r.returncode: print(name, r.stderr[-2000:]); sys.exit(1)
    return total

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
    for name in (sys.argv[1:] or ADS):
        out = OUTD + f"Gloves_Retarget_{name}.mp4"
        build(name, ADS[name], 0, out)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        print("OK", name, round(build(name, ADS[name], round(-14 - I, 1), out), 2), "s")
